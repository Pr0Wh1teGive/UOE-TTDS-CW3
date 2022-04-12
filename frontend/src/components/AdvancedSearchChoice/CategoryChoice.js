import "./AdvancedSearchChoice.css"
import React, {useState} from "react";
import {Checkbox, FormControl, ListItemText, MenuItem, Select} from "@mui/material";

const MenuProps = {
    PaperProps: {
        style: {
            width: 250,
            maxHeight: 250,
        },
    },
};

const categoryNames = [
    "business",
    "tech",
    "politics",
    "sport",
    "entertainment",
];

function CategoryChoice( {getCategory} ) {

    const [categoryName, setCategoryName] = useState([]);
    const handleChange = (event) => {
        const {
            target: { value },
        } = event;
        setCategoryName(
            typeof value === "string" ? value.split(",") : value,
        );
        getCategory(event.target.value);
    };

    return (
        <div>
            <FormControl sx={{ m: 1, width: 250, backgroundColor: "#fff", borderRadius: "4px", margin: 0}} size="small" color="success">
                <Select
                    fullWidth
                    id="category-multiple-checkbox"
                    multiple
                    displayEmpty
                    value={categoryName}
                    onChange={handleChange}
                    renderValue={(selected) => {
                        if (selected.length === 0) {
                            return <em className="search_placeholder">Category</em>;
                        }
                        return selected.join(", ");
                    }}
                    MenuProps={MenuProps}
                >
                    {categoryNames.map((name) => (
                        <MenuItem key={name} value={name}>
                            <Checkbox checked={categoryName.indexOf(name) > -1} color="success"/>
                            <ListItemText primary={name}/>
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
        </div>
    );
}

export default CategoryChoice;
