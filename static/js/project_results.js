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
};

let loaded_pr = () => {
    let input = document.getElementById("project_minutes");
    let feels = document.getElementsByName("feels");

    for (let i = 0; i < feels.length; i++) {
        feels[i].addEventListener("change", feels_update);
    }
};

if (document.readyState === "complete")
    loaded_pr();
else
    document.addEventListener("DOMContentLoaded", loaded_pr);
