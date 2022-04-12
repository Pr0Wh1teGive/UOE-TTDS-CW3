import "./App.css";
import "./components/SearchContainer/SearchContainer.css"
import React, {Component, Fragment} from "react";
import API from "./utils/API";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import Search from "./components/Search/Search";
import NewsDisplay from "./components/NewsDisplay/NewsDisplay";
import SearchError from "./components/SearchError/SearchError";

// import "./backend/database.py" as databas

class App extends Component {
    constructor(pros) {
        super(pros);
        this.state = {
            news: [],
            searchStatus: [], // there are three search status: success, noResults, error
        };
    }

    componentDidMount() {
        this.setState({ searchStatus: [] });
    };

    // do the search, interact with the backend by POST, the data type is JSON
    searchWork = (data) => {
        const {searchInput, dateFrom, dateTo, source, category} = data;

        this.setState( { searchStatus: [] }, async  () => {
            try {
                // toBackend: json {Search:str, StartTime:str, EndTime:str, Source:list(str), Category:list(str) }
                const searchResult = await API.post("/searching",
                    {"Search": searchInput, "StartTime": dateFrom, "EndTime": dateTo, "Source": source, "Category": category});
                const resultData = searchResult.data;
                // const resultData = [2000];
                // print the search results from backend
                // return list {json {Title:title, Date:date, Source:source, Abstract:abstract, Category:category, URL:url} }
                console.log(resultData);
                if (resultData.length === 0) {
                    this.setState({searchStatus: "noResults"});
                } else {
                    // const db = database.DBConnector();
                    // const returnData = db.find_news_by_ids(resultData);
                    // console.log(returnData);
                    // this.setState( { news: returnData} );
                    this.setState( {news: resultData} );
                    console.log(this.state.news);
                    this.setState({ searchStatus: "success"} );
                }
            } catch (error) {
                console.error(error);
                this.setState( {searchStatus: "error"} );
            }
        });
    }


    render() {
        const { news, searchStatus } = this.state;
        return (
            <div className="App">
                <Header />
                <section className="searchContainer">
                    <div className="searchContainer_container">
                        <div className="searchContainer_title">
                            <h1 className="searchContainer_title-heading">
                                Search News
                            </h1>
                            <p className="searchContainer_title-description">
                                Input keywords to search the latest news
                            </p>
                        </div>
                        <Search
                            searchWork={this.searchWork}
                        />
                    </div>
                </section>
                <section className="main_content">
                    <Fragment>
                        { searchStatus === "success" && <NewsDisplay searchData={news} /> }
                    </Fragment>
                </section>
                {searchStatus === "error" && <SearchError type="error" />}
                {searchStatus === "noResults" && <SearchError type="noResults" />}
                <Footer />
            </div>
        );
    }
}

export default App;
