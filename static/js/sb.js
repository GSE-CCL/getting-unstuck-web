loaded_sb = () => {
    if (typeof have_loaded_sb == "undefined") {
        let script = document.createElement("script");
        script.onload = function () {
            scratchblocks.renderMatching("code.sb", {
                inline: true,
                style: "scratch3"
            });
            scratchblocks.renderMatching("code._sb", {
                inline: false,
                style: "scratch3"
            });
        };
        script.src = "https://scratchblocks.github.io/js/scratchblocks-v3.4-min.js";
        document.head.appendChild(script);

        have_loaded_sb = true;
    }
    else {
        scratchblocks.renderMatching("code.sb", {
            inline: true,
            style: "scratch3"
        });
        scratchblocks.renderMatching("code._sb", {
            inline: false,
            style: "scratch3"
        });
    }
};

if (document.readyState === "complete")
    loaded_sb();
else
    document.addEventListener("DOMContentLoaded", loaded_sb);
