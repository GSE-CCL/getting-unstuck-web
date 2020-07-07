let feels_update = (event) => {
    let MAX_FEELS = 5;
    let feels = get_checked_feels();
    if (feels.length > MAX_FEELS) {
        event.target.checked = false;
        document.getElementById("feels_instructions").classList.add("font-weight-bold", "text-danger");
    }
    else {
        document.getElementById("feels_instructions").classList.remove("font-weight-bold", "text-danger");
    }

    submit_form();
};

let get_checked_feels =  () => {
    let feels = document.getElementsByName("feels");
    let checked = [];

    for (let i = 0; i < feels.length; i++) {
        if (feels[i].checked) {
            checked.push(feels[i].value);
        }
    }

    return checked;
};

let init_reflection = () => {
    let pid = get_id(window.location.href);
    let saved = (Cookies.get("_reflections") === undefined) ? {} : saved = JSON.parse(Cookies.get("_reflections"));

    if (pid in saved) {
        document.getElementById("project_minutes").value = saved[pid]["minutes"];
        set_checked_feels(saved[pid]["feelings"]);

        let evt1 = new Event("input");
        document.getElementById("project_minutes").dispatchEvent(evt1);

        let evt2 = new Event("change");
        document.getElementById("project_minutes").dispatchEvent(evt2);
    }
    
    // Hide if needed
    handle_ajax("GET", "/project/o/" + pid, {}, (ret) => {
        if (!(ret.response == "" || ret.response == Cookies.get("_gu_uid")) || !navigator.cookieEnabled) {
            document.getElementById("project_reflection").classList.add("d-none");
        }
    });
};

let set_checked_feels = (checked) => {
    let feels = document.getElementsByName("feels");

    for (let i = 0; i < feels.length; i++) {
        if (checked.includes(feels[i].value)) {
            feels[i].checked = true;
        }
    }
};

let submit_form = () => {
    let data = {
        minutes: document.getElementById("project_minutes").value,
        feelings: get_checked_feels()
    };

    let id = get_id(window.location.href);
    let reflections = (Cookies.get("_reflections") === undefined) ? {} : JSON.parse(Cookies.get("_reflections"));
    reflections[id] = data;
    Cookies.set("_reflections", JSON.stringify(reflections), {expires: 30});

    let url = "/project/f/" + id;
    handle_ajax("POST", url, data, () => {}, "json");
};


let loaded_pr = () => {
    let time = document.getElementById("project_minutes");
    let feels = document.getElementsByName("feels");

    for (let i = 0; i < feels.length; i++) {
        feels[i].addEventListener("change", feels_update);
    }

    time.addEventListener("change", submit_form);

    init_reflection();
};

if (document.readyState === "complete")
    loaded_pr();
else
    document.addEventListener("DOMContentLoaded", loaded_pr);
