import "./NewsDisplay.css";
import React, {Component} from "react";
import {Grid} from "@mui/material";
import EachNewsDisplay from "../EachNewsDisplay/EachNewsDisplay";
import Pagination from "material-ui-flat-pagination";

class NewsDisplay extends Component {
    constructor(props) {
        super(props);
        this.state = {
            searchData: [],
            numberPerPage: 10,
            currentPage: 0,
        };
    }

    handlePageClick = (currentPage) => { this.setState({currentPage: currentPage}) };

    render() {
        const { numberPerPage, currentPage } = this.state;
        const { searchData } = this.props;
        return (
            <div>
                <Grid item xs={6}>
                    <h6 className="search_results_text">
                        {`Search Results: ${searchData.length} news`}
                    </h6>

                    {searchData.length > numberPerPage &&
                        <Pagination
                            limit={numberPerPage}
                            total={searchData.length}
                            offset={currentPage}
                            page={currentPage}
                            onClick={(event, currentPage) => this.handlePageClick(currentPage)}
                        />
                    }

                    {searchData.slice(currentPage, currentPage + numberPerPage).map((eachNews, idx) =>
                        <EachNewsDisplay key={idx} {...eachNews}/>
                    )}

                    {searchData.length > numberPerPage &&
                        <Pagination
                            limit={numberPerPage}
                            total={searchData.length}
                            offset={currentPage}
                            page={currentPage}
                            onClick={(event, currentPage) => this.handlePageClick(currentPage)}
                        />
                    }

                    <div className="display_bottom">
                    </div>

                </Grid>
            </div>
        );
    }
}

export default NewsDisplay;
