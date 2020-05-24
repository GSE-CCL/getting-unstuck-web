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
