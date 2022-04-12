import "./AdvancedSearch.css";
import React, {useState} from "react";
import {Collapse, FormControlLabel, Switch} from "@mui/material";
import DatePicker from "../DatePicker/DatePicker";
import CategoryChoice from "../AdvancedSearchChoice/CategoryChoice";
import SourceChoice from "../AdvancedSearchChoice/SourceChoice";

function AdvancedSearch({ getDateFromAd, getSourceFromAd, getCategoryFromAd, getCollapsedFromAd}) {

    const [isCollapsed, setIsCollapsed] = useState(false);

    const handleClick = () => {
        setIsCollapsed((prev) => (!prev));
        console.log(isCollapsed)
        getCollapsedFromAd(isCollapsed)
        getDateFromAd("","");
        getSourceFromAd([]);
        getCategoryFromAd([]);
    };

    // get date input from component DatePicker by function
    const getDate  = (getDateFrom, getDateTo) => {
        getDateFromAd(getDateFrom, getDateTo);
    };

    const getSource  = (getSource) => {
        getSourceFromAd(getSource);
    };

    const getCategory = (getCategory) => {
        getCategoryFromAd(getCategory);
    };


    return (
        <div className="advanced_search">
            <FormControlLabel
                control={<Switch checked={isCollapsed} onChange={handleClick} color="success"/>}
                label={<p className="advanced_search_button">
                    Advanced Search
                </p>}
            />
            <Collapse in={isCollapsed}>
                <div className="advanced_search_container">
                    <h5 className="advanced_search_title">
                        Time Range
                    </h5>
                    { isCollapsed && <DatePicker getDate={getDate} /> }
                    <h5 className="advanced_search_title">
                        Choose Source
                    </h5>
                    { isCollapsed && <SourceChoice getSource={getSource} /> }
                    <h5 className="advanced_search_title">
                        Choose Category
                    </h5>
                    { isCollapsed && <CategoryChoice getCategory={getCategory} /> }
                </div>
            </Collapse>
        </div>
    );
}

export default AdvancedSearch;
