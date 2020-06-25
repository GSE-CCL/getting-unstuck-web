let loaded_sb = () => {
    if (window.location.href.indexOf("/view")  == -1) {
    handle_ajax("GET", window.location + "/view", {}, (e) => {
        window.location += "/view"
    }, type="form");
    }
};

if (document.readyState === "complete")
    loaded_sb();
else
    document.addEventListener("DOMContentLoaded", loaded_sb);
