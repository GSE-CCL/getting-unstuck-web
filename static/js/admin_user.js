let loaded = function() {
    // How to recreate user actions
    let actions = function(identifier) {
        let html = '<a href="#" data-action="edit" data-identifier="' + identifier + '" title="Edit" class="fa fa-edit"></a> \
                    <a href="#" data-action="reset_password" data-identifier="' + identifier + '" title="Reset Password" class="fa fa-key"></a> ';
        if (identifier != document.getElementById("user_greeting").dataset.identifier) {
            html += '<a href="#" data-action="delete" data-identifier="' + identifier + '" title="Delete" class="fa fa-trash"></a>'
        }

        return html;
    };

    // Field types
    let fields = {
        "first_name": {"type": "text", "name": "First name", "required": "required"},
        "last_name": {"type": "text", "name": "Last name", "required": "required"},
        "username": {"type": "text", "name": "Username", "required": "required"},
        "email": {"type": "email", "name": "Email", "required": "required"},
        "password": {"type": "password", "name": "Password", "required": "required"},
        "role": {"type": "select", "name": "Role", "options": ["site_admin", "site_viewer"], "required": "required"},
        "__url__": "/admin/users",
        "__identifier__": "username",
        "__type__": "user",
        "__actions__": actions
    };

    // Page-specific events
    let reset_pw_event = (event) => {
        let identifier = event.target.dataset.identifier;
        enableModal(fields, event, ["username", "password"], "reset_password", "Reset password", {"username": identifier});
        
        if (identifier == "") 
            document.querySelector(".modal-body #username").focus();
        else
            document.querySelector(".modal-body #password").focus();
    };

    // Set page-specific events
    let page_events = function() {
        let reset_pw_buttons = document.querySelectorAll("[data-action='reset_password']");
        reset_pw_buttons.forEach(btn => {
            btn.removeEventListener("click", reset_pw_event);
            btn.addEventListener("click", reset_pw_event);
        });
    };
    document.addEventListener("page_events", page_events);

    // Set the events!
    setEvents(fields);
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);