# In this script, the functions and classes used for
# connecting the MySQL database is defined and explained.

# Based on different search content<String>, entity <Dict>
# should be returned
import json
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, exc

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

########################################################################################
#  START OF TABLE CONFIGURATIONS

# Table for the mapping relation between category label and its id
# Example: {id: 4, category: 'business'}
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(15), unique=True)

# Table for the mapping relation between name of news source and its id
# Example: {id: 1, source: 'nytime'}
class NewsSource(db.Model):
    __tablename__ = 'newsSource'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(15), unique=True)

# Table for the news records.
# Example: {id: 1, data: 2022-03-14, title: 'Sample Title', content: 'Sample Content',
#           category_id: 4, source_id: 1, link: 'https://www.nytimes.com/....'}
class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DATE)
    title = db.Column(db.String(500))
    content = db.Column(db.TEXT)  # this attribute contains the concatenated 'description' and 'content' fragments of raw news data.
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    source_id = db.Column(db.Integer, db.ForeignKey('newsSource.id'), nullable=True)
    link = db.Column(db.TEXT)
    __table_args__ = (UniqueConstraint('date', 'title', name='unique_title_per_day'),)

class NewsLen(db.Model):
    __tablename__ = 'newsLen'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), unique=True)
    length = db.Column(db.Integer)

# Table for the vocabulary for indexing.
# Example: {id: 3, vocab: 'university'}
class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    id = db.Column(db.Integer, primary_key=True)
    vocab = db.Column(db.String(25), unique=True)

# Table for inverted position index (i.e. the appearance position of each vocabulary token in each article)
# Example: {id: 18, vocab_id: 3, news_id: 5, pos: '2;4;6;'}
#           means the token 'university' appeared in the 2nd, 4th and 6th position in news record whose id is 5
class IndexPos(db.Model):
    __tablename__ = 'indexPos'
    id = db.Column(db.Integer, primary_key=True)
    vocab_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    pos = db.Column(db.TEXT)  # a string of positions concatenated with ';', e.g. '3;5;15;120;'
    __table_args__ = (UniqueConstraint('vocab_id', 'news_id', name='unique_cons'),)

# Table for inverted frequency index (i.e. the times of appearance of each vocabulary token in each article)
# Example: {id: 19, vocab_id: 3, news_id: 5, frq: 3, in_title: True}
#           means the token 'university' appeared for 3 times in the news record whose id is 5,
#           and we know it appeared at least once in the title of this news article.
class IndexFrq(db.Model):
    __tablename__ = 'indexFrq'
    id = db.Column(db.Integer, primary_key=True)
    vocab_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))
    frq = db.Column(db.Integer)
    in_title = db.Column(db.BOOLEAN, default=False)  # whether this token appeared in the title of this news
    __table_args__ = (UniqueConstraint('vocab_id', 'news_id', name='unique_cons'),)

#  END OF TABLE CONFIGURATIONS
########################################################################################


class DBConnector:
    def __init__(self):
        host = '127.0.0.1'
        port = 3306
        username = 'root'
        password = 'gatewayttds'
        db_name = 'TTDS'
        connect_str = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(username, password, host, port, db_name)
        app.config['SQLALCHEMY_DATABASE_URI'] = connect_str
        self.cate2id_map = None
        self.id2cate_map = None

    def initialize_db(self):
        """
        This function will create the tables in database on the server, and insert some initial records into them.
        This function should be called in following cases:
        1. the structure of some table is changed (and the relative table in database is dropped)
        2. add a new table (defined by a new db.Model class in this script)
        """
        db.create_all()
        source1 = NewsSource(id=1, source='nytimes')
        source2 = NewsSource(id=2, source='bbc')
        source3 = NewsSource(id=3, source='reuters')
        try:
            db.session.add_all([source1, source2, source3])
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(type(e))
            db.session.rollback()

    def source2id(self, source_name):
        """[tested]
        Map the name of news sources to the source id in 'newsSource' table.
        (the records in 'newsSource' table is set manually according to the mapping relation defined in this function)
        :param source_name: the name of a news source.
        :return: the corresponding news id.
        """
        source_id = 0
        if source_name == "nytimes":
            source_id = 1
        elif source_name == "bbc":
            source_id = 2
        elif source_name == "reuters":
            source_id = 3
        return source_id

    def id2source_long(self, source_id):
        """[tested]
        Convert the source id to whole source name.
        This function is used to support the front side display of news source information
        The resulted name is the whole source name (e.g. "New York Times")
                instead of abbreviation used in database (e.g. "nytimes")
        :param source_id:
        :return:
        """
        source_name = "Unknown"
        if source_id == 1:
            source_name = "New York Times"
        elif source_id == 2:
            source_name = "BBC News"
        elif source_id == 3:
            source_name = "Reuters"
        return source_name

    def category2id(self, category_label):
        """[tested]
        Map the category labels (String) to category ids (Integer) according to 'category' table in database.
        To reduce the query time, the first calling of this function will store the whole mapping in local memory.
        Later calling on this function has no need to query the database. (Same mechanism for id2category() )
        :param category_label: a String of category
        :return: the corresponding category id
        """
        category_id = -1
        # fetch the mapping from database
        if self.cate2id_map is None:
            self.cate2id_map = {}
            try:
                categories = db.session.query(Category).all()
                for category_record in categories:
                    self.cate2id_map[category_record.category] = category_record.id
            except exc.SQLAlchemyError as e:
                print("-- Error in fetching category-id mapping " + e)
                db.session.rollback()
        # use the local mapping to convert to id
        if category_label in self.cate2id_map.keys():
            return self.cate2id_map[category_label]
        return category_id

    def id2category(self, category_id):
        """[tested]
        Convert a category_id to category label.
        """
        category_label = "unknown"
        # fetch the mapping from database
        if self.id2cate_map is None:
            self.id2cate_map = {}
            try:
                categories = db.session.query(Category).all()
                for category_record in categories:
                    self.id2cate_map[category_record.id] = category_record.category
            except exc.SQLAlchemyError as e:
                print("-- Error in fetching id-category mapping " + e)
                db.session.rollback()
        # use the local mapping to convert to id
        if category_id in self.id2cate_map.keys():
            return self.id2cate_map[category_id]
        return category_label

    def convert_to_dictionary(self, obj):
        """
        Convert a db.Model entity to Dictionary entity.
        :param obj: db.Model entity
        :return: corresponding Dictionary entity.
        """
        record = dict({
            "id": obj.id,
            "date": obj.date,
            "title": obj.title,
            "content": obj.content,
            "category_id": obj.category_id,
            "source_id": obj.source_id,
            "link": obj.link
        })
        return record

    ########################################################################################
    # Functions for fetching news records from database ####################################

    def find_records(self, start_date=None, end_date=None, category_list=None, source_list=None):
        """[tested]
        Fetch news records from database, only considers the time, category and source constraints.
        :param start_date: starting date for the time constraint, in the format of 'YYYY-MM-DD', this data is included in search range.
        :param end_date: ending date for the time constraint, in the format of 'YYYY-MM-DD', this data is included in search range.
        :param category: a list of categories in Strings (e.g. ['arts', 'business'], or ['u.s.'])
        :param source_list: a list of news sources in Strings, the available source labels are: 'bbc' and 'nytimes'
        :return: a list of news records, each as db.Model instance, whose information can be accessed via ".attr" method
        Notice: the category and newsSource information in returned records are id instead of labels,
        further work is required to convert them into String labels (either by JOIN in DB operation, or Dictionary at local)
        """
        if start_date == None: start_date = '1970-01-01'
        if end_date == None: end_date = db.func.current_date()
        # convert category labels to category id
        if category_list != None:
            category_query_result = db.session.query(Category).filter(Category.category.in_(category_list))
            category_id_list = [record.id for record in category_query_result]
        # convert source labels to source id
        if source_list != None:
            souce_id_list = [self.source2id(s) for s in source_list]
        res = db.session.query(News).filter(db.and_(
            News.date >= start_date,
            News.date <= end_date,
            News.category_id.in_(category_id_list) if category_list is not None else db.text(''),
            News.source_id.in_(souce_id_list) if source_list is not None else db.text('')
            # News.category == category if category else db.text(''),
            # News.source_id == self.source2id(source) if source else db.text('')
            )
        ).all()
        return res

    def find_news_by_ids(self, news_ids):
        """[tested]
        Search a single news or multiple news records based on given id / ids.
        Notice: in the result the category_id and source_id have been automatically mapped to labels.
        :param news_ids: the id(s) of news. This can be a single id (i.e. int) or a list of ids
        :return: a list of Dictionary entities with following keys: id, date, title, content, category, source, link
        """
        if news_ids is None: return []
        if isinstance(news_ids, int): news_ids = [news_ids]
        res = []
        for news_id in news_ids:
            try:
                record = db.session.query(News).filter(News.id == news_id).first()
                if record is None:
                    print("-- News with id=" + str(news_id) + " is not found")
                    continue
                res.append({
                    "id": record.id,
                    "date": record.date,
                    "title": record.title,
                    "content": record.content,
                    "category": self.id2category(record.category_id),
                    "source": self.id2source_long(record.source_id),
                    "link": record.link
                })
            except exc.SQLAlchemyError as e:
                print("-- Error in fetching news with id=" + news_id + " " + e)
                db.session.rollback()
        # res = db.session.query(News).filter_by(id=news_id).first()
        return res

    def pull_news_batch(self, start_id, num):
        """[tested]
        Pull a specified number of records starting from a specified news id.
        If the news records with start_id not exists, return the news records starting from the next existing id.
        This function is mainly used for the data collection for the following cases:
            (1) train models based on news records in database
            (2) fetch records from database and predict their category, then update relative columns
            (3) construct index for news records in database
        :param start_id: the starting point of records pulling, included in the returned record list
        :param num: the batch size, number of news records to be pulled from database
        :return: a list of Dictionary entities, each is a news record with the following attributes: id, title, content
        """
        records = db.session.query(News).filter(News.id>=start_id).order_by(db.asc(News.id))[:num]
        res = [{"id": record.id, "title": record.title, "content": record.content} for record in records]
        return res

    #######################################################################################
    # Functions for news length update ####################################################

    def update_existing_length(self):
        start_id = 0
        end_id = 0
        batch_size = 1000
        news_batch = self.pull_news_batch(start_id, batch_size)
        while len(news_batch) > 0 and news_batch[-1]["id"] != end_id:
            end_id = news_batch[-1]["id"]
            start_id = end_id + 1
            for news in news_batch:
                news_id = news["id"]
                length = len(news["content"].split())
                try:
                    db.session.add(NewsLen(
                        news_id=news_id,
                        length=length
                    ))
                    db.session.commit()
                except exc.SQLAlchemyError as e:
                    print("Fail to add length record for article=" + str(news_id))
                    print(type(e))
                    db.session.rollback()
            print("finished length update until news_id: " + str(end_id))
            news_batch = self.pull_news_batch(start_id, batch_size)

    def get_news_length_for_ids(self, ids):
        res = {}
        for news_id in ids:
            try:
                record = db.session.query(NewsLen).filter(NewsLen.news_id == news_id).first()
                if record is None:
                    print("-- News with id=" + str(news_id) + " is not found")
                    continue
                res[news_id] = record.length
            except exc.SQLAlchemyError as e:
                print("-- Error in fetching news with id=" + news_id + " " + e)
                db.session.rollback()
        return res

    def insert_news_length(self, news_id_length):
        """
        news_id_length: a Dictionary {news_id<Integer> : news_article_length<Integer>}
        """
        for news_id, length in news_id_length.items():
            try:
                db.session.add(NewsLen(
                    news_id=news_id,
                    length=length
                ))
                db.session.commit()
            except exc.SQLAlchemyError as e:
                print("Fail to add length record for article=" + str(news_id))
                print(type(e))
                db.session.rollback()


    ########################################################################################
    # Functions for upload news records into database ######################################

    def upload_local_files(self, news_source="nytimes"):
        """
        The crawler will fetch and store the news data in local files.
        This function will upload these news records into database.
        :param news_source: the source of news, this is also the directory name of local dataset.
        """
        relative_dataset_path = "dataset"
        news_file_root_path = os.path.join(relative_dataset_path, news_source, "2021")
        print(news_file_root_path)

        news_count, error_count, duplicate_count = 0, 0, 0
        max_des, max_title, max_content, max_link = 0, 0, 0, 0

        for path, dir_list, file_list in os.walk(news_file_root_path):
            for file_name in file_list:
                if file_name == "articles":
                    with open(os.path.join(path, file_name)) as f:
                        json_file = json.load(f)
                        print(os.path.join(path, file_name) + " ---- " + str(len(json_file['articles'])) + " files")
                        news_count += len(json_file['articles'])
                        default_date = path[-8:]
                        for article in json_file['articles']:
                            if article['section'] == None:
                                category = db.null
                            else:
                                category = (article['section'].split('&')[0]).lower()
                                category = db.null if category == 'null' else category
                            if article['published_date'] == None:
                                date = default_date
                            else:
                                date_lower = (article['published_date']).lower()
                                date = default_date if (date_lower == 'null' or date_lower == 'none') else str(
                                    article['published_date'])[0:10]
                            new_article = News(
                                date=date,
                                title=article['title'],
                                content=article['description'] + " " + article['content'],
                                source_id=self.source2id(news_source),
                                link=article['link']
                            )
                            max_des = max(max_des, len(article['description']))
                            max_link = max(max_link, len(article['link']))
                            max_title = max(max_title, len(article['title']))
                            max_content = max(max_content, len(article['content']))

                            try:
                                dup = db.session.query(News).filter_by(date=date).filter_by(
                                    title=article['title']).first()
                                if not dup:
                                    db.session.add(new_article)
                                    db.session.commit()
                                else:
                                    duplicate_count += 1
                            except exc.SQLAlchemyError as e:
                                error_count += 1
                                print(type(e))
                                db.session.rollback()
                        print("--- finished")

        print("====== Transfer finished with " + str(news_count) + " news ======")
        print(str(error_count) + " error occurs, " + str(duplicate_count) + " duplicates are ignored")
        print("max_title: " + str(max_title))
        print("max_des: " + str(max_des))
        print("max_content: " + str(max_content))
        print("max_link: " + str(max_link))

    def upload_records(self, news_records):
        """[tested]
        This function should be used in two cases:
        (1) Upload the pre-processed (e.g. remove non-English news) initial dataset into database:
            In this case, the 'category' column will be set to default null value.
            After the category-classification model is trained, the 'category' attributes of all database news records
            will be updated manually via upload_category_list() and update_record_category() functions.
        (2) Incremental update of newly fetched news records:
            i.e. fetch the updated news from news website every day, preprocess them and upload into database.
            In this case, assume the 'category' information is uploaded along with the news record.
        :param news_records: a list of news records, each as a Dictionary entity as the following keys and value types:
                            date: String
                            title: String
                            content: String
                            (category: Integer for category id accords to 'category' table in database
                                       String for category labels       ) --> this attribute is optional
                            source:   Integer for news source id accords to 'newsSource' table in database
                                      String for news source labels, i.e. one of "nytimes" or "bbc"
                            link: String
                Notice: (1) if category has not be determined, the news Dictionary can discard the key "category"
                        (2) for "category" and "source" attributes, both id or label input are supported
                e.g. news_records = [ {date:..., title:..., ...} , {date:..., title:..., ...} , ...  ]
        """
        for news_record in news_records:
            category = None
            if "category" in news_record.keys():
                category = news_record["category"] if isinstance(news_record["category"], int) else self.category2id(news_record["category"])
            try:
                db.session.add(News(
                    date=news_record["date"],
                    title=news_record["title"],
                    content=news_record["content"],
                    category_id=category,
                    source_id=news_record["source"] if isinstance(news_record["source"], int) else self.source2id(news_record["source"]),
                    link=news_record['link']
                ))
                db.session.commit()
            except exc.SQLAlchemyError as e:
                print("Fail to insert article: (" + news_record["date"] + ") " + news_record["title"])
                print(type(e))
                print("-- Possible reason: duplic print(type(e))ation in database")
                db.session.rollback()
        return

    ########################################################################################
    # Functions for Index uploading and fetching ###########################################

    def upload_index(self, index_dict):
        """[tested]
        After the inverted index is built over a batch of news records,
        use this function to store the vocabulary and index into tables in database.
        - This function supports a dynamic vocabulary, which means the function
          will automatically insert records of the new vocabulary tokens into 'vocabulary' table.
        - For each token-article pair in the input list,
          two corresponding records will be inserted into 'IndexPos' and 'IndexFrq' separately.
        :param index_dict: a <Dictionary> entity whose key is vocabulary token,
                            value is <Dictionary> of news id - list of positions pairs
                            { vocab(String) : {news_id(Integer):[pos1,pos2,...],
                                                news_id(Integer):[pos1,pos2,...], ...},
                              ... }
        :return: number of failed insertion operations (that may caused by duplication)
        """
        for vocab, news_pos_dict in index_dict.items():
            # (1) check whether this token (vocab) has been recorded in 'vocabulary' table of database, store it if not
            # (2) get the vocabulary id of this token, which will be used in following index record insertion
            vocab_id = self.vocab2id(vocab)
            if vocab_id == -1:
                try:
                    db.session.add(Vocabulary(vocab=vocab))
                    db.session.commit()
                    vocab_id = self.vocab2id(vocab)
                except exc.SQLAlchemyError as e:
                    print("Adding vocabulary (" + vocab + ") failed ! " + str(type(e)))
                    db.session.rollback()
            # Skip and report if failed to get the vocab_id
            if vocab_id == -1:
                print("----- Skip the insertion of index records related to vocab: " + vocab + " -----")
                continue

            # Insert index records for all articles with respect to the current token (i.e. vocab)
            for news_id, pos_list in news_pos_dict.items():
                # (1) concatenate the appearance positions of this token in this news article into a string split by ';'
                pos_string = ""
                for pos in pos_list:
                    pos_string += (str(pos) + ";")
                # (2) upload the vocab_id-news_id-string into indexPos table
                # (3) upload the vocab_id-news_id-frequency into indexFrq table
                try:
                    pos_idx = IndexPos(vocab_id=vocab_id, news_id=news_id, pos=pos_string)
                    frq_idx = IndexFrq(vocab_id=vocab_id, news_id=news_id, frq=len(pos_list), in_title=(pos_list[0]<200))
                    db.session.add(pos_idx)
                    db.session.add(frq_idx)
                    db.session.commit()
                except exc.SQLAlchemyError as e:
                    print("Insertion (" + vocab + " - article " + str(news_id) + ") failed ! " + str(type(e)))
                    db.session.rollback()
        return

    def search_position_index(self, vocab_list, news_id_list=None):
        """[tested]
        Search the position index records for the input vocab list,
        within the range of news articles identified by the given news id list.
        :param vocab_list: a list of pre-processed tokens.
        :param news_id_list: (optional) a list of news_ids, the returned index must related to one of these ids.
        :return: a Dictionary of vocabulary and corresponding indices:
                    { vocab(String) : [[news_id, pos_string],
                                       [news_id, pos_string], ... ]
                    }
        """
        res = {}
        for vocab in vocab_list:
            res[vocab] = []
            vocab_id = self.vocab2id(vocab)
            try:
                if news_id_list is None:
                    indices = db.session.query(IndexPos).filter_by(vocab_id=vocab_id).all()
                else:
                    indices = db.session.query(IndexPos).filter(IndexPos.news_id.in_(news_id_list)).filter_by(vocab_id=vocab_id).all()
                for index_record in indices:
                    res[vocab].append([index_record.news_id, index_record.pos])
            except exc.SQLAlchemyError as e:
                print("Failed to fetch position index for (" + vocab + ") ! " + str(type(e)))
                db.session.rollback()
        return res

    def search_frequency_index(self, vocab_list, news_id_list=None):
        """[tested]
        Search the frequency index records for the input vocab list,
        within the range of news articles identified by the given news id list.
        :param vocab_list: a list of pre-processed tokens.
        :param news_id_list: (optional) a list of news_ids, the returned index must related to one of these ids.
        :return: a Dictionary of vocabulary and corresponding indices:
                    { vocab(String) : [[news_id, frequency],
                                       [news_id, frequency], ... ]
                    }
        """
        res = {}
        for vocab in vocab_list:
            res[vocab] = []
            vocab_id = self.vocab2id(vocab)
            try:
                if news_id_list is None:
                    indices = db.session.query(IndexFrq).filter_by(vocab_id=vocab_id).all()
                else:
                    indices = db.session.query(IndexFrq).filter(IndexFrq.news_id.in_(news_id_list)).filter_by(vocab_id=vocab_id).all()
                for index_record in indices:
                    res[vocab].append([index_record.news_id, index_record.frq])
            except exc.SQLAlchemyError as e:
                print("Failed to fetch frequency index for (" + vocab + ") ! " + str(type(e)))
                db.session.rollback()
        return res

    def search_index(self, vocab_list, index_type="pos", start_date=None, end_date=None, category_list=None, source_list=None, news_id_list=None):
        """[tested]
        A comprehensive index search function that fetches the index record for specified tokens,
        and also considers the constraints of date, category,news source,
        and supports only search within specified news_article id list.
        Guidance of use case:
            (1) when front-end pass the query and constraints, use this function to execute the initial index search;
                in this initial search, all the date / category / news source conditions are applied.
            (2) when the filtering of phrase/proximity search is completed, and get a list of news ids as search range,
                in this case: please use the previous functions search_frequency_index() and search_position_index(),
                since they are more lightweight and only involves one table, so they should cost less time.
        :param vocab_list: a list of pre-processed tokens.
        :param index_type: Compulsory, one of "frq" and "pos"
        :param start_date: (optional)
        :param end_date: (optional)
        :param category_list: (optional)
        :param source_list: (optional)
        :param news_id_list: (optional)  a list of news_ids, the returned index must related to one of these ids.
        :return: when index_type =="pos":
                    { vocab(String) : [[news_id(Integer), position_string(String)],
                                       [news_id(Integer), position_string(String)], ... ]
                    }
                when index_type =="frq":
                { vocab(String) : [[news_id(Integer), in_title(Boolean), frequency(Integer)],
                                   [news_id(Integer), in_title(Boolean), frequency(Integer)], ... ]
                }
        """
        if start_date == None: start_date = '1970-01-01'
        if end_date == None: end_date = db.func.current_date()
        if category_list != None:
            category_query_result = db.session.query(Category).filter(Category.category.in_(category_list))
            category_id_list = [record.id for record in category_query_result]
        if source_list != None:
            souce_id_list = [self.source2id(s) for s in source_list]

        res = {}
        indexClass = IndexPos if index_type=="pos" else IndexFrq

        print("!!!!!!!!!Search Index!!!!!!!!!")
        print(vocab_list)
        for vocab in vocab_list:
            print("!!!!!!!!!!!!!!!!!!")
            print(vocab)
            print("------------------")
            res[vocab] = []
            vocab_id = self.vocab2id(vocab)
            try:
                indices = db.session.query(indexClass, News).filter(db.and_(
                        # filter index by given id list
                        indexClass.news_id.in_(news_id_list) if news_id_list is not None else db.text(''),
                        # consider the constraint on date range, category, news source
                        News.date >= start_date,
                        News.date <= end_date,
                        News.category_id.in_(category_id_list) if category_list is not None else db.text(''),
                        News.source_id.in_(souce_id_list) if source_list is not None else db.text(''),
                        # join, based on the news articles within range
                        indexClass.news_id == News.id,
                        # filter the
                        indexClass.vocab_id == vocab_id
                    )).all()
                for index_record in indices:
                    if index_type == "pos":
                        res[vocab].append([index_record[0].news_id, index_record[0].pos])
                    else:
                        res[vocab].append([index_record[0].news_id, index_record[0].in_title==1, index_record[0].frq])
            except exc.SQLAlchemyError as e:
                print("Failed to fetch frequency index for (" + vocab + ") ! " + str(type(e)))
                db.session.rollback()
        return res

    ####################################################################################################
    # Functions for fetching from vocabulary table (update of vocabulary is done in upload_index()) ####

    def get_vocab_id_map(self, vocab_list):
        """[tested]
        Get a mapping between vocabulary tokens and their ids for the input vocabulary list.
        Notice: If some input vocabulary token is not recorded in database,
                these tokens will not appear in the returned Dictionary!
        :param vocab_list: a list of tokens.
        :return: a Dictionary with tokens as keys, ids as values.
        """
        mapping = {}
        records = db.session.query(Vocabulary).filter(Vocabulary.vocab.in_(vocab_list)).all()
        for record in records:
            mapping[record.vocab] = record.id
        return mapping

    def vocab2id(self, vocab):
        """[tested]
        Search the id of a vocabulary token in database.
        :param vocab: a pre-processed token.
        :return: -1 if the vocabulary not in database, otherwise the vocab_id.
        """
        vocab_record = db.session.query(Vocabulary).filter_by(vocab=vocab).first()
        if not vocab_record:
            return -1
        else:
            return vocab_record.id

    ########################################################################################
    # Functions for updating category information in database ##############################

    def upload_category_list(self, category_list):
        """ [tested]
        After the category-classification model is trained, this function should be called
        to upload the whole list of all possible categories into the 'category' table in database.
        :param category_list: a list of category labels: [String, String, ...]
        :return:
        """
        for category in category_list:
            try:
                db.session.add(Category(category=category))
                db.session.commit()
            except exc.SQLAlchemyError as e:
                print("-- Duplicate category: " + category + " -- ignored")
                db.session.rollback()
        # this function may changed the category mappings, so initialize the local mappings
        self.cate2id_map = None
        self.id2cate_map = None
        return

    def update_record_category(self, news_cate_pairs):
        """ [tested]
        This function should be called after the category-classification model.
        :param news_cate_pairs: a list of pairs: [<news_id:Integer, category_label:String>, ... ]
        """
        # (1) pull the category table from database, construct Dictionary from category label to category id
        cate2id = {}
        cate_records = db.session.query(Category).all()
        for record in cate_records:
            cate2id[record.category] = record.id
        # (2) iterate over input pairs, add the UPDATE query into session
        for pair in news_cate_pairs:
            if pair[1] not in cate2id.keys():
                print("-- Unexpected category label for article "
                      + str(pair[0]) + ": '" + pair[1] + "' is not recorded in database --")
                continue
            try:
                db.session.query(News).filter(News.id==pair[0]).update({'category_id': cate2id[pair[1]]})
                db.session.commit()
            except exc.SQLAlchemyError as e:
                print("Failed to update category_id of news_id=" + pair[0] + "  " + e)
                db.session.rollback()
        return

# function for test
if __name__ == '__main__':
    db_connector = DBConnector()
    # db_connector.upload_local_files()

    print("============================================================================")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    """
    Test: find_records()
    find news records with time, category, source constraints
    """
    # for article in db_connector.find_records(start_date='2021-12-22', end_date='2021-12-23', source_list=["bbc", "reuters"]):
    #     print(str(article.id) + " " + str(article.date) + " " + ("null" if article.category_id is None else str(article.category_id)) + " --> " + article.title[0:30])

    """
    Test: upload_category_list()
    upload all possible categories into the 'category' table in database
    """
    # cate_labels = ["business", "nature", "sports", "science", "game", "u.s.", "world"]
    # db_connector.upload_category_list(cate_labels)

    """
    Test: update_record_category()
    update category of existing news records
    """
    # cate_list = []
    # cate_list.append([48523, "business"])
    # cate_list.append([48494, "unknown"])
    # cate_list.append([48613, "u.s."])
    # db_connector.update_record_category(cate_list)

    """
    Test: pull_news_batch()
    fetch a batch of records with consecutive ids,starting from a given id
    """
    # news_batch = db_connector.pull_news_batch(1117, 10)
    # for news in news_batch:
    #     print(str(news["id"]) + ": " + news["title"] + "\n\t" + news["content"][0:100])

    """
    Test: find_news_by_ids()
    fetch a batch of arbitrary records based on given id(s)
    """
    # print(db_connector.find_news_by_ids(48604))
    # print(db_connector.find_news_by_ids([48523, 48613]))
    # print(db_connector.find_news_by_ids(12))

    """
    Test: upload_index()
    Upload the index into IndexPos and IndexFrq.
    """
    # index = {
    #     "spring": {48523: [1, 10, 25, 73, 102, 203], 48613: [2, 10], 48604: [15, 23, 27, 28]},
    #     "edinburgh": {48523: [3, 13, 29], 48613: [12, 89, 111, 119, 151], 48604: [2, 13, 17]}
    # }
    # index = {
    #     "spring": {48523: [1], 48613: [2, 10], 48494: [1, 2, 3, 4, 5]},
    #     "flight": {48523: [1, 9, 19, 29], 48613: [2, 8, 18, 28]}
    # }
    # db_connector.upload_index(index)

    """
    Test: search_position_index() & search_frequency_index()
    """
    # frq_index = db_connector.search_frequency_index(["edinburgh", "bus", "flight"])
    # for token, article_list in frq_index.items():
    #     print(token + ":")
    #     for article in article_list: print("-- " + str(article[0]) + ": " + str(article[1]))
    # pos_index = db_connector.search_position_index(["edinburgh", "bus", "flight"])
    # print("-----------------------")
    # for token, article_list in pos_index.items():
    #     print(token + ":")
    #     for article in article_list: print("-- " + str(article[0]) + ": " + article[1])

    """
    Test: upload_records()
    """
    # news_list = [
    #     {
    #         "date": "1968-01-02", "title": "Today is a good day", "content": "Since it is sunny.",
    #         "category": "sun", "source": "bbc", "link": "https://goodday.ccomm"
    #      },
    #     {
    #         "date": "1968-01-04", "title": "Today is a bad day", "content": "Since it is not sunny!",
    #         "category": 11, "source": 1, "link": "https://goodday.ccomm"
    #     },
    #     {
    #         "date": "1968-01-06", "title": "Today is a normal day", "content": "Since it is shining",
    #         "source": "bbc", "link": "https://goodday.ccomm"
    #     },
    # ]
    # db_connector.upload_records(news_list)
    # for article in db_connector.find_records(start_date='1968-01-01', end_date='1968-01-29'):
    #     print(str(article.id) + " " + str(article.date) + " "
    #           + ("null" if article.category_id is None else db_connector.id2category(article.category_id)) + " "
    #           + ("null" if article.source_id is None else db_connector.id2source_long(article.source_id))
    #           + " --> " + article.title[0:30])

    """
    Test: get_vocab_id_map
    """
    # res = db_connector.get_vocab_id_map(["edinburgh", "spring", "flight", "toilet"])
    # print(res)

    """
    Test: search_position_index() & search_frequency_index(), updated: search within given news_id list
    """
    # index = {
    #     "edinburgh": {50486: [1], 50481: [2, 10], 50496: [1, 2, 3, 4, 5]},
    #     "bus": {50486: [1], 50481: [2, 10]}
    # }
    # db_connector.upload_index(index)
    # print("index uploaded")
    # news_id_list = [0, 1000, 48604, 48523, 2000, 50481, 50486]
    # frq_index = db_connector.search_frequency_index(["edinburgh", "bus", "flight"], news_id_list=news_id_list)
    # for token, article_list in frq_index.items():
    #     print(token + ":")
    #     for article in article_list: print("-- " + str(article[0]) + ": " + str(article[1]))
    # print("-----------------------")
    # pos_index = db_connector.search_position_index(["edinburgh", "bus", "flight"], news_id_list=news_id_list)
    # for token, article_list in pos_index.items():
    #     print(token + ":")
    #     for article in article_list: print("-- " + str(article[0]) + ": " + article[1])

    """
    Test: search_index()
    """
    # news_id_list = [0, 1000, 48604, 48523, 2000, 50481, 50486]
    # news_id_list = []

    # frq_index = db_connector.search_index(index_type="frq", vocab_list=["edinburgh", "bus", "flight"], news_id_list=news_id_list)
    # for token, article_list in frq_index.items():
    #     print(token + ":")
    #     for article in article_list: print("-- " + str(article[0]) + ": " + str(article[1]))
    # print("========================================")

    # frq_index = db_connector.search_index(index_type="frq",vocab_list=["edinburgh", "bus", "winter"])
    # for token, article_list in frq_index.items():
    #     print(token + ":")
    #     for article in article_list: print("-- " + str(article[0]) + ": " + str(article[1]) + " " + str(article[2]))
    # print("--------------")
    # pos_index = db_connector.search_index(index_type="pos", vocab_list=["edinburgh", "bus", "winter"])
    # for token, article_list in pos_index.items():
    #     print(token + ":")
    #     for article in article_list: print("-- " + str(article[0]) + ": " + str(article[1]))

    # db_connector.initialize_db()
    db_connector.update_existing_length()
    # res = db_connector.get_news_length_for_ids([117628,114626])
    # print(res)

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("============================================================================")