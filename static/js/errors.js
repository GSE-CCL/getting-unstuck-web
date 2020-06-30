let loaded = () => {
    // Field types
    let fields = {
        "error_id": {"type": "text", "name": "Error ID", "required": "required"},
        "__url__": "/admin/errors",
        "__identifier__": "error_id",
        "__type__": "error",
        "__actions__": () => {}
    };

    // Set the events!
    setEvents(fields);
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
