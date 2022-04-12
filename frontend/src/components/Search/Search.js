import "./Search.css";
import React, {Component} from 'react';
import Button from "../Button/Button";
import AdvancedSearch from "../AdvancedSearch/AdvancedSearch";

class Search extends Component {
    constructor(props) {
        super(props);
        this.state = {
            searchInput: "",
            dateFrom: "",
            dateTo: "",
            source: [],
            category: [],
            collapsed: true,
        };
    }

    componentDidMount() {
        this.setState({ searchInput: "" });
    };

    // if the input is the hint, "please input the word!", reset the input when focus
    handleFocus = (event) => {
        const inputNull = "please input the word!";
        const searchInput = event.target;
        if (searchInput.value === inputNull) {
            searchInput.closest("form").reset();
        }
    }

    // when submitting, the input can not be empty
    handleSubmit = async (event) => {
        event.preventDefault();
        const inputNull = "please input the word!";
        const textInput = event.target.search;
        // bug: if user input "please input the word!", the search won't work
        if (textInput.value === inputNull) {
            return;
        }
        // whether there is input (the input can not be empty)
        if (!textInput.value.trim()) {
            textInput.value = inputNull;
            return;
        }
        else {
            await this.setState({ searchInput: textInput.value });
            if (this.state.collapsed === true) {
                await this.setState({dateFrom: "", dateTo: "", source: [], category: []})
            }
            const {searchInput, dateFrom, dateTo, source, category, collapsed} = this.state;
            // pass all the input by user to function searchWork
            console.log(collapsed)
            console.log(searchInput, dateFrom, dateTo, source, category)
            this.props.searchWork({searchInput, dateFrom, dateTo, source, category});
        }
    }

    // get the date (from and to)
    getDateFromAd = async (dateFromParam, dateToParam) => {
        await this.setState({ dateFrom: dateFromParam});
        await this.setState({ dateTo: dateToParam});
        console.log(this.state.dateFrom);
        console.log(this.state.dateTo);
    }

    // get the source chosen by user
    getSourceFromAd = async (sourceParam) => {
        await this.setState({ source: sourceParam});
        console.log(this.state.source);
    }

    //get the category chosen by user
    getCategoryFromAd = async (categoryParam) => {
        await this.setState({ category: categoryParam});
        console.log(this.state.category);
    }

    getCollapsedFromAs = async (collapsedStatus) => {
        await this.setState({ collapsed: collapsedStatus});
    }

    render() {
        return (
            <div>
                <form className="search" onSubmit={this.handleSubmit} noValidate>

                    <AdvancedSearch
                        getDateFromAd={this.getDateFromAd}
                        getSourceFromAd={this.getSourceFromAd}
                        getCategoryFromAd={this.getCategoryFromAd}
                        getCollapsedFromAd={this.getCollapsedFromAs}
                    />

                    <input
                        type="text"
                        name="search"
                        className="search_input"
                        placeholder="please enter a search topic here"
                        onFocus={this.handleFocus}
                        required
                    />

                    <Button buttonClass="button_type_text search_button" type="submit">
                        Search
                    </Button>

                </form>
            </div>
        );
    }
}

export default Search;
