import "./Header.css"
import React from "react";
import {HashRouter, Link} from "react-router-dom";
import returnTop from "../returnTop";

function Header() {
    return (
        <header className="header">
            <div className="header_container">
                <HashRouter>
                    <Link className="header_title" to="/" onClick={returnTop}>
                        <div className="header_title_text">
                            NewsTTDS
                        </div>
                    </Link>
                </HashRouter>
            </div>
        </header>
    );
}

export default Header;
