import "./Footer.css";
import React from "react";
import {HashRouter, Link} from "react-router-dom";
import returnTop from "../returnTop";

function Footer() {
    return (
        <footer className="footer">
            <div className="footer_container">
                <p className="footer_copyright">
                    2022 TTDS Coursework
                </p>
                <li className="footer_home">
                    <HashRouter>
                        <Link to="/" onClick={returnTop} className="footer_home_link">
                            Home
                        </Link>
                    </HashRouter>
                </li>
            </div>
        </footer>
    );
}

export default Footer;
