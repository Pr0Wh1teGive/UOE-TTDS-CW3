# TTDS Group Project (News Search Engine Ver 1.0.0)  
Update date: 3/24/2022  
This is the group project for TTDS at University of Edinburgh  
The work contained in the report is original and has been done by our team  
And any work from this project is not permitted to be submitted to any places by anyone else  

# Project Structure
- data_fetch/news_crawler: the currently used crawler for collecting news data from the web.
- front-end: contains the front-end part written by ReactJS.
- input: contains stop words from nltk and csv files for training the news categorizer.
- model: contains the trained model for predicting news' categorize.
- database.py: contains the database table configuration and APIs for database communication.  
- engine.py: where search function is defined and to obtain index from database
- support.py: where all functions to support search is defined, including boolean search, proximity search, phrase search, TFIDF ranking.  
- pipeline.py: contains the whole process from loading local news data to uploading indices to the database.  
- preprocessing.py: contains functions for performing preprocess on the title and content of raw news data.  

# Groups:
Group A:  Frontend   
Group B:  Backend  
Group C:  Database  

# Group contributors:
A - Yongjian Liu   
A - Jiayu Xue  
B - Jiwei Zhang   
B - Xuanhua Yin  
C - Guangdi Hu  
C - Weichen Zhu  

# Work principles:
1: Clone the project into your local directory. "git clone [Repository URL]"   
2: Each group leader create your development branch "git checkout -b group_name master"  
3: You are supposed to work on your owrn branch. "git checkout -b your_branch group_name"  
4: Your branch can only be merged to your group branch, after being reviewed by the group leader  
5: Please create pull request for branch merge on github for a review by others.  
6: A group -> master merge MUST be reviewed by any other group leader before it is merged.  

# Frontend <-> Engine
function "search()"  
params: content:str, start:str(2021-03-25), end:str(2021-03-25), source:list(str), category:list(str)  
return list [news_id]  
