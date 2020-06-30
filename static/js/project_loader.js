let loaded = () => {
    setTimeout(() => {
        document.getElementById("message").innerText = "Hmmm. This is taking awhile. Contact us if this takes much longer.";
    }, 10000);

    if (window.location.href.indexOf("/view")  == -1) {
        handle_ajax("GET", window.location + "/view", {}, (e) => {
            window.location += "/view";
        }, type="form");
    }
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
