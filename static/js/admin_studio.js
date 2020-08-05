let loaded = function() {
    // How to recreate user actions
    let actions = function(identifier) {
        let html = '<a href="#" data-action="delete" data-identifier="' + identifier + '" title="Delete" class="fa fa-trash"></a>'
        return html;
    };

    // Field types
    let fields = {
        "studio_id": {"type": "text", "name": "Studio ID", "required": "required"},
        "challenge_id": {"type": "select", "name": "Prompt Schema", "options": challenge_schemas, "required": ""},
        "__url__": "/admin/studios",
        "__identifier__": "studio_id",
        "__type__": "studio",
        "__actions__": actions
    };

    // Page-specific event: choose schema
    let choose_schema = (event) => {
        let identifier = event.target.dataset.identifier;
        enableModal(fields, event, ["studio_id", "challenge_id"], "choose_schema", "Choose schema", {"studio_id": identifier});
        
        if (identifier == "")
            document.querySelector(".modal-body #studio_id").focus();
        else
            document.querySelector(".modal-body #challenge_id").focus();
    };

    // Page-specific event: redownload studio
    let redownload = (event) => {
        let identifier = event.target.dataset.identifier;
        let data = {
            "studio": identifier,
            "schema": "__none__",
            "show": null
        };
        handle_ajax("POST", "/studio", data, () => {
            alert("Initiated redownload.");
        }, type="form");
    };

    // Page-specific event: revalidate studio
    let revalidate = (event) => {
        let identifier = event.target.dataset.identifier;
        let data = {
            "action": "revalidate",
            "studio": identifier,
            "schema": "__none__"
        };
        handle_ajax("POST", "/admin/studios", data, () => {
            alert("Initiated revalidation.");
        }, type="form");
    };

    // Set page-specific events
    let page_events = function() {
        let choose_schema_buttons = document.querySelectorAll("[data-action='choose_schema']");
        choose_schema_buttons.forEach(btn => {
            btn.removeEventListener("click", choose_schema);
            btn.addEventListener("click", choose_schema);
        });

        let redownload_buttons = document.querySelectorAll("[data-action='redownload']");
        redownload_buttons.forEach(btn => {
            btn.removeEventListener("click", redownload);
            btn.addEventListener("click", redownload);
        });

        let revalidate_buttons = document.querySelectorAll("[data-action='revalidate']");
        revalidate_buttons.forEach(btn => {
            btn.removeEventListener("click", revalidate);
            btn.addEventListener("click", revalidate);
        });
    };
    document.addEventListener("page_events", page_events);

    // Set the events
    setEvents(fields);

    // Toggle challenge page visibility.
    let togglers = document.querySelectorAll("[data-action='toggle_publicity']");
    togglers.forEach((toggler) => {
        toggler.addEventListener("click", (event) => {
            let data = {
                action: "set_public_show",
                identifier: event.target.parentNode.parentNode.dataset.identifier
            };

            handle_ajax("POST", fields["__url__"], data, (res) => {
                if (res.response == "true") {
                    let was_true = event.target.dataset.to == "True";
                    event.target.dataset.to = was_true ? "False" : "True";
                    let span = document.querySelector("tr[data-identifier='" + data["identifier"] + "'] [data-field='public_show'] span");
                    
                    if (was_true) {
                        span.classList.remove("fa-times");
                        span.classList.add("fa-check");
                    }
                    else {
                        span.classList.remove("fa-check");
                        span.classList.add("fa-times");
                    }
                }
                else {
                    alert("I couldn't toggle the publicity for this.");
                }
            });
        });
    });
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
