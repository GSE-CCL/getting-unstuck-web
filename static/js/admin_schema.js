let toggleDetails = (event) => {
    let affects = event.target.dataset.actionId;
    if (event.target.dataset.current == "show") {
        document.getElementById(affects).style.display = "none";
        event.target.dataset.current = "hide";
        event.target.innerText = "Show";
    }
    else {
        document.getElementById(affects).style.display = "block";
        event.target.dataset.current = "show";
        event.target.innerText = "Hide";
    }
};

let loaded = () => {
    // Delete basically
    // How to recreate user actions
    let actions = function(identifier) {
        let html = '<a href="#" data-action="delete" data-identifier="' + identifier + '" title="Delete" class="fa fa-trash"></a>'
        return html;
    };

    // Field types
    let fields = {
        "schema_id": {"type": "text", "name": "Schema ID", "required": "required"},
        "__url__": "/admin/schemas",
        "__identifier__": "schema_id",
        "__type__": "schema",
        "__actions__": actions
    };

    // Set the events!
    setEvents(fields);

    // Event for showing/hiding schema details
    let showmores = document.querySelectorAll("[data-action='show']");
    showmores.forEach((showmore) => {
        showmore.addEventListener("click", toggleDetails);
    });
};


if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
