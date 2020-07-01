// A function that does the same thing as scratchblocks.renderMatching, but exports PNG!
renderMatchingPNG = (selector, options) => {
    let objs = document.querySelectorAll(selector);
    objs.forEach(obj => {
        let code = scratchblocks.read(obj, options);
        var doc = scratchblocks.parse(code, options);
        var docView3 = scratchblocks.newView(doc, options);

        docView3.render();
        docView3.exportPNG((url) => {
            let img = new Image();
            img.src = url;
            img.alt = code;
            img.addEventListener("load", () => {
                img.width *= .8;
            });
            
            obj.innerHTML = "";
            obj.appendChild(img);
        }, 1);
});
};

loaded_sb = () => {
    if (typeof have_loaded_sb == "undefined") {
        let script = document.createElement("script");
        script.onload = function () {
            renderMatchingPNG("code._sb", {
                inline: false,
                style: "scratch3"
            });
            renderMatchingPNG("code.sb", {
                inline: true,
                style: "scratch3"
            });
        };
        script.src = "https://scratchblocks.github.io/js/scratchblocks-v3.5-min.js";
        document.head.appendChild(script);

        have_loaded_sb = true;
    }
    else {
        renderMatchingPNG("code.sb", {
            inline: true,
            style: "scratch3"
        });
        renderMatchingPNG("code._sb", {
            inline: false,
            style: "scratch3"
        });
    }
};

if (document.readyState === "complete")
    loaded_sb();
else
    document.addEventListener("DOMContentLoaded", loaded_sb);
