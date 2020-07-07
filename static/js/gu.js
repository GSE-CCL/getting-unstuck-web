// Get project ID from URL
let get_id = (text) => {
    text = text.replace("/editor", "");
    text = text.replace("/view", "");

    let tokenized = text.split("/");
    let i = tokenized[tokenized.length - 1] == ""
            ? tokenized.length - 2
            : (tokenized.length - 1);

    if (i < 0) return -1;
    else {
        let res = parseInt(tokenized[i]);
        if (isNaN(res)) return -1;
        else return res;
    }
};

// Handle AJAX
let handle_ajax = function(method, url, data, callback, type="form") {
    let datas = new URLSearchParams(data)

    var http = new XMLHttpRequest();
    http.onreadystatechange = function() {
        if (this.readyState == 4) {
            callback(this);
        }
    };
    http.open(method, url, true);

    if (type == "form") {
        http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        http.send(datas.toString());
    }
    else if (type == "json") {
        http.setRequestHeader("Content-type", "application/json");
        http.send(JSON.stringify(data));
    }
};

// Adapted from https://stackoverflow.com/a/1349426/6062385
let strgen = (length) => {
    let result = "";
    let characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
};

// Toggles navbar on mobile
let toggle_navbar = (event) => {
    let selector = event.target.dataset.target;
    let element = document.querySelector(selector);

    element.classList.toggle("collapse");
};


let init_gu = () => {
    if (Cookies.get("_gu_uid") === undefined) {
        Cookies.set("_gu_uid", strgen(128), {expires: 60});
    }

    let navs = document.getElementsByClassName("navbar-toggler");
    for (let i = 0; i < navs.length; i++) {
        navs[i].addEventListener("click", toggle_navbar);
    }
};


if (document.readyState === "complete")
    init_gu();
else
    document.addEventListener("DOMContentLoaded", init_gu);