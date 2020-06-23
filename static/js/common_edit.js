// Post AJAX
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
}

// Add JS to page
let add_js = function(src) {
    var script = document.createElement("script");
    script.src = src;
    document.head.appendChild(script);
};

// Get radio value
let get_radio = function(radios) {
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            return radios[i].value;
        }
    }

    return null;
}

// Disable # links
let hash_links = document.querySelectorAll("a[href='#']");
hash_links.forEach(link => {
    link.addEventListener("click", (event) => {
        event.preventDefault();
    });
});
