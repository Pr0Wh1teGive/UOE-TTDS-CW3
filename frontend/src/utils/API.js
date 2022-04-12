import axios from "axios";

export default axios.create({
    baseURL: 'http://35.189.108.218:5000/',
    responseType: 'json'
})