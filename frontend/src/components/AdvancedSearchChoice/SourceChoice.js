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

const sourceNames = [
    "New York Times",
    "BBC News",
];

function SourceChoice( {getSource} ) {

    const [sourceName, setSourceName] = useState([]);
    const handleChange = (event) => {
        const {
            target: { value },
        } = event;
        setSourceName(
            typeof value === "string" ? value.split(",") : value,
        );
        getSource(event.target.value);
    };

    return (
        <div>
            <FormControl sx={{ m: 1, width: 250, backgroundColor: "#fff", borderRadius: "4px", margin: 0}} size="small"  color="success">
                <Select
                    fullWidth
                    id="source-multiple-checkbox"
                    multiple
                    displayEmpty
                    value={sourceName}
                    onChange={handleChange}
                    renderValue={(selected) => {
                        if (selected.length === 0) {
                            return <em className="search_placeholder">Source</em>;
                        }
                        return selected.join(", ");
                    }}
                    MenuProps={MenuProps}
                >
                    {sourceNames.map((name) => (
                        <MenuItem key={name} value={name}>
                            <Checkbox checked={sourceName.indexOf(name) > -1} color="success"/>
                            <ListItemText primary={name}/>
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
        </div>
    );
}

export default SourceChoice;
