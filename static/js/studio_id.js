// Get project ID from URL
let get_id = (text) => {
    text = text.replace("/editor", "");
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

let find_project = (event) => {
    event.preventDefault();

    let identifier = document.getElementById("identifier").value;
    let id = get_id(identifier);

    let index = -1;
    if (identifier == "") {
        index = -1;
    }
    else if (authors.includes(identifier)) {
        index = authors.indexOf(identifier);
    }
    else if (project_ids.includes(id)) {
        index = project_ids.indexOf(id);
    }
    else {
        for (let i = 0; i < titles.length; i++) {
            if ( titles[i].includes(identifier)) {
                index = i;
                break;
            }
        }
    }

    if (index < 0) {
        let msg = document.getElementById("find_project_alert");
        msg.innerHTML = 'Couldn&rsquo;t find that project!';
        msg.classList.remove("hide");

        if (id > -1) {
            msg.innerHTML += ' We&rsquo;re downloading it now though and will redirect if it works!';
            let studio_id = document.getElementById("studio_id").value;
            let data = {
                "sid": studio_id,
                "pid": id
            }
            handle_ajax("POST", "/project/d", data, (res) => {
                if (res.responseText == "True") {
                    window.location = "/project/" + id;
                }
                else {
                    msg.innerHTML = "Unfortunately, we couldn&rsquo;t download that project.";
                }
            }, type="form")
        }
    }
    else {
        window.location = "/project/" + project_ids[index];
    }
};

let loaded = () => {
    let form = document.getElementById("find_project");
    form.addEventListener("submit", find_project);
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);