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
