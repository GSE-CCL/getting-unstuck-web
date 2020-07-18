// Global data variable for summary page
let data = null;

// Get a stat given a slash-separated identifier and a nested object of stats
let get_stat = (identifier, stats) => {
    let parts = identifier.split("/");
    let value = stats;
    for (let i = 0; i < parts.length; i++) {
        value = value[parts[i]];
    }

    return value;
};

// Replace the stat placeholders on the page with the actual stats
let replace_stats = (stats) => {
    // Inline stats
    let elements = document.getElementsByClassName("stat");
    for (let i = 0; i < elements.length; i++) {
        elements[i].innerText = get_stat(elements[i].innerText, stats);
    }

    // Stat rows (gray background)
    let containers = document.getElementsByClassName("stat_row");
    for (let i = 0; i < containers.length; i++) {
        let stats = JSON.parse(containers[i].innerText);
        containers[i].innerHTML = "";

        for (let j = 0; j < stats.length; j++) {
            let html = '<div class="col-md text-center py-3"><h1 class="gastromond">'
            if (stats[j][0][0] == "$") {
                let x = get_stat(stats[j][0].substring(1), data);

                if (x !== undefined) {
                    html += x.toLocaleString();
                }
                else {
                    html += "?";
                }
            }
            else {
                html += stats[j][0].toLocaleString();
            }
            html += '</h1><p class="my-0">' + stats[j][1]
            html += '</p></div>'

            containers[i].innerHTML += html;
        }
    }
};

// Get the data from the server
let get_data = (cb) => {
    if (data === null) {
        handle_ajax("POST", "/summary", {}, (res) => {
            data = JSON.parse(res.responseText);
            replace_stats(data);

            if (cb !== null) {
                cb(data);
            }
        });
    }
    else {
        if (cb !== null) {
            cb(data);
        }
    }

    return data;
};


// Initialize graphics
let init_graphics = () => {
    // Country map
    let countries_data = d3.map();
    for (nation in data["nations"]) {
        countries_data.set(nation, data["nations"][nation]);
    }

    country_map(countries_data);

    // Project counts over time
    let projects_data = [];
    for (let i = 0; i < data["project_counts"].length; i++) {
        // Exclude day 0
        if (data["project_counts"].length == 11 && i == 0) {
            continue;
        }
        else {
            let a = d3.map();
            a.set("key", "Day " + i);
            a.set("value", data["project_counts"][i]);
            projects_data.push(a);
        }
    }

    bar_graph(projects_data, "project-graph", "Daily studio", "Projects");

    // Prior Scratch experience graph
    let experience_data = [];
    for (exp in data["static"]["experience"]) {
        let a = d3.map();
        a.set("key", exp);
        a.set("value", data["static"]["experience"][exp]);
        experience_data.push(a);
    }

    let blue = (d) => { return "#5dc7e4" };

    bar_graph(experience_data, "experience-graph", "Scratch experience", "People", blue, {x: 30, y: 30}, -6);

    // Block category totals graph
    let categories_data = [];
    for (cat in data["totals"]["categories"]) {
        let a = d3.map();
        a.set("key", cat);
        a.set("value", data["totals"]["categories"][cat])
        categories_data.push(a);
    }

    let choose_color = (d) => {
        // From https://github.com/heyjessi/getting-unstuck-visual/blob/master/js/main.js#L166
        if (d.get("key") === "motion"){
            return "#4681db";
        }
        if (d.get("key") === "control") {
            return "#f2ab1d"
        }
        if (d.get("key") === "event") {
            return "#ffcb3f"
        }
        if (d.get("key") === "looks") {
            return "#965ffc"
        }
        if (d.get("key") === "operator") {
            return "#4faa49"
        }
        if (d.get("key") === "sensing") {
            return "#66b2d6"
        }
        if (d.get("key") === "sound") {
            return "#ca70d8"
        }
        if (d.get("key") === "data") {
            return "#ef7b28"
        }
        if (d.get("key") === "procedures") {
            return "#f75976"
        }
    };

    bar_graph(categories_data, "categories-graph", "Block category", "Total number of blocks", choose_color, {x: 50, y: 30});
};

// Get data and then initialize graphs
let p = new Promise((resolve, reject) => {
    get_data(resolve);
}).then((d) => {
    init_graphics();
});

// Change opacity of stitched image
let opacity_full = (e) => {
    e.target.style.opacity = 1
};

let opacity_half = (e) => {
    e.target.style.opacity = .5
};

let loaded_sum = () => {
    let img = document.getElementById("img");
    img.addEventListener("mouseenter", opacity_full);
    img.addEventListener("mouseleave", opacity_half);
};

if (document.readyState === "complete")
    loaded_sum();
else
    document.addEventListener("DOMContentLoaded", loaded_sum);
