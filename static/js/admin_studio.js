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

    // Set the events!
    setEvents(fields);
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
