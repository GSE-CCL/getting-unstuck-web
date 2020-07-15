let loaded_sg = () => {
    var projects = [];
    
    var gallery = new Vue({
        el: ".gallery",
        delimiters: ["<%", "%>"],
        data: {
            batch_size: 32,
            more: true,
            page: 0,
            projects: projects,
            rows: Math.ceil(projects.length / 4)
        },
        methods: {
            get_projects: function(n) {
                return this.projects.slice(n * 4, n * 4 + 4);
            },
            load_more: function() {
                let cb = (response) => {
                    let ps = JSON.parse(response.response);
                    for (let i = 0; i < ps["projects"].length; i++) {
                        projects.push(ps["projects"][i]);
                    }
                    this.rows = Math.ceil(this.projects.length / 4);
                    this.page += 1;

                    if (ps["projects"].length < this.batch_size) {
                        this.more = false;
                    }
                };

                let uri = "/studio/list/" + get_id(window.location.href) + "?page=" + this.page + '&limit=' + this.batch_size;
                handle_ajax("GET", uri, {}, cb);
            },
            truncate: function(text, length) {
                if (text.length < length) return text;
                else return text.slice(0, length + 1) + "...";
            }
        },
        created: function () {
            this.load_more();
        }
    });
};

if (document.readyState === "complete")
    loaded_sg();
else
    document.addEventListener("DOMContentLoaded", loaded_sg);


