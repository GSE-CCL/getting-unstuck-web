let loaded = function() {
    // How to recreate user actions
    let actions = function(identifier) {
        let html = '<a href="#" data-action="delete" data-identifier="' + identifier + '" title="Delete" class="fa fa-trash"></a>'
        return html;
    };

    // Field types
    let fields = {
        "studio_id": {"type": "text", "name": "Studio ID", "required": "required"},
        "__url__": "/admin/studios",
        "__identifier__": "studio_id",
        "__type__": "studio",
        "__actions__": actions
    };

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
