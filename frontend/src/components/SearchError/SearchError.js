import "./SearchError.css";
import React from "react";

function SearchError({ type }) {
    return (
        <div className="no_results">
            {type === "noResults" && (
                <>
                    <h2 className="no_results_title">
                        No Results
                    </h2>
                    <p className="no_results_text">
                        It seems that there is no news related ot the keyword.
                    </p>
                </>
            )}
            {type === "error" && (
                <>
                    <h2 className="no_results_title no_results_title_error">
                        Error
                    </h2>
                    <p className="no_results_text no_results_text_error">
                        An error occurred during the search request.
                    </p>
                </>
            )}
        </div>
    );
}

export default SearchError;
