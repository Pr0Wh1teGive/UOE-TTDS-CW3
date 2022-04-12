import "./EachNewsDisplay.css";
import React, {Component} from "react";
import {Card, CardActionArea, CardContent} from "@mui/material";

class EachNewsDisplay extends Component {
    openNewsPage = (URL) => {
        try {
            console.log(URL);
            window.open(`${URL}`);
        } catch (error) {
            console.error(error);
        }
    };


    render() {
        const { title, date, source, content, category, link} = this.props;

        console.log(content.trim().split(/\s+/).length)
        // console.log(content.trim().split(/\s+/))

        return (
            <div>
                <Card className="news_card">
                    <CardActionArea onClick={ () => this.openNewsPage(link)} className="news_display">
                        <CardContent className="each_news_container">
                            <h1 className="each_news_title"> {title} </h1>
                            <div className="each_news_information">
                                <h4 className="each_news"> {date} </h4>
                                <h4 className="each_news"> {source} </h4>
                                <h4 className="each_news"> {category} </h4>
                            </div>
                            { content.trim().split(/\s+/).length < 100 &&  <h3 className="each_news_abstract"> {content} </h3>}
                            { content.trim().split(/\s+/).length >= 100 &&
                                <h3 className="each_news_abstract"> {content.trim().split(" ",100).join(" ") + "..."} </h3>}
                        </CardContent>
                    </CardActionArea>
                </Card>
            </div>
        );
    }
}

export default EachNewsDisplay;
