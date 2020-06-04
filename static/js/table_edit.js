/** Table row editor code
    *********************

    The following functions facilitate turning rows
    in a table into forms, such that they can be edited
    in place.
   
    To use, simply call setEvents(fields) where fields
    is an associative array like this:
    
    fields = {
        "username": {"type": "text"},
        "email": {"type": "email"},
        "role": {"type": "select", "options": ["site_admin", "site_viewer"]},
        "__url__": "/admin/users",
        "__identifier__": "username",
        "__type__": "user",
        "__actions__": actions
    };

    Here, username, email, and role are all fields in the table.
    Their type attributes represent their form types as
    should be displayed. For the role field, it's a select
    type, so options are provided as an array.

    __url__ is the POST URL for the form.
    
    __identifier__ tells us which field is the unique one in the table.
    Your table should have a data-identifier attribute on each row,
    and each edit button should have data-identifier and data-action "edit".

    __type__ is a string representing the type of object we are working with.

    __actions__ is a function describing how to get the links or buttons to be
    displayed in the table's "Actions" column for a given row, given the identifier
    of that row.
**/

// Generate a form element
let generateFormElement = function(field, fields, defaultValue="", label) {
    let html = "";

    if ((field.match(/__/g) || []).length == 2) {
        return html;
    }

    if (label === true) {
        html += '<label for="' + field + '">' + fields[field]["name"] + '</label>';
    }

    if (fields[field]["type"] == "text"
        || fields[field]["type"] == "email"
        || fields[field]["type"] == "password") {
        
        html += '<input type="' + fields[field]["type"]
               + '" ' + fields[field]["required"] + ' class="form-control mb-2" name="'
               + field + '" id="' + field + '" value="' + defaultValue + '" placeholder="'
               + fields[field]["name"] + '">';
    }
    else if (fields[field]["type"] == "select") {
        html += '<select name="' + field + '" class="form-control mb-2" '
                + fields[field]["required"] + ' id="' + field + '">';
        if (Array.isArray(fields[field]["options"])) {
            fields[field]["options"].forEach(option => {
                html += '<option value="' + option + '"';

                if (option == defaultValue)
                    html += " selected";

                html += '>' + option + '</option>';
            });
        }
        else {
            for (let [key, value] of Object.entries(fields[field]["options"])) {
                html += '<option value="' + key + '"';

                if (key == defaultValue)
                    html += " selected";
                
                html += '>' + value + '</option>';
            }
        }
        html += '</select>';
    }

    return html;
}

// Disable the row editor
let disableEditor = function(fields, data) {
    let identifier = data[fields["__identifier__"]];
    let row = document.querySelector("tr[data-identifier='" + data["identifier"] + "']");
    row.dataset.identifier = identifier;

    for (let i = 0; i < row.children.length; i++) {
        field = row.children[i].dataset.field;
        if (field in fields) {
            row.children[i].innerText = data[field];
        }
        else if (field == "actions") {
            row.children[i].innerHTML = fields["__actions__"](identifier);
        }
    }
    setEvents(fields);
};

// Enable the row editor
let enableEditor = function(fields, event) {
    let identifier = event.target.dataset.identifier;
    let row = document.querySelector("tr[data-identifier='" + identifier + "']");
    let existing_information = {"identifier": identifier};

    for (let i = 0; i < row.children.length; i++) {
        field = row.children[i].dataset.field;
        if (field in fields) {
            existing_information[field] = row.children[i].innerText;
            row.children[i].innerHTML = generateFormElement(field, fields, row.children[i].innerText, false);
        }
        else if (field == "actions") {
            row.children[i].innerHTML = '<button class="btn btn-primary fa fa-save" data-action="save" data-identifier="'
                                        + identifier +'"></button>'
                                        + '<button class="btn btn-secondary fa fa-times" data-action="cancel" data-identifier="'
                                        + identifier + '"></button>';
            row.children[i].children[0].addEventListener("click", (event) => {
                saveRow(fields, event);
            });
            row.children[i].children[1].addEventListener("click", (event) => {
                disableEditor(fields, existing_information);
            });
        }
    }
};

// Save a row
let saveRow = function(fields, event) {
    let identifier = event.target.dataset.identifier;
    let row = document.querySelector("tr[data-identifier='" + identifier + "']");
    let data = {"identifier": identifier, "action": "edit"};

    for (let i = 0; i < row.children.length; i++) {
        field = row.children[i].dataset.field;
        if (field in fields) {
            let input = row.children[i].children[0];
            if ("required" in input.attributes && input.value == "") {
                data = false;
                break;
            }
            else
            {
                data[field] = input.value;
            }
        }
    }
    
    if (data == false) {
        alert("All fields are required.");
    }
    else {
        handle_ajax("POST", fields["__url__"], data, (e) => {
            if (e.readyState == 4 && e.status == 200) {
                if (e.responseText == "true")
                    disableEditor(fields, data);
                else if (e.responseText == "false")
                    alert("Couldn't edit row.");
                else
                    alert("Couldn't edit row - " + JSON.parse(e.responseText) + ".");
            }
        });
    }
};

// Add a row
let addRow = function(fields, data) {
    let model = document.querySelector("tr[data-identifier='__model__']");
    let html = '<tr data-identifier="' + data["identifier"] + '">';

    for (let i = 0; i < model.children.length; i++) {
        field = model.children[i].dataset.field;
        if (field in data) {
            html += '<td data-field="' + field + '">' + data[field] + "</td>";
        }
        else if (field == "actions") {
            html += '<td data-field="actions">' + fields["__actions__"](data["identifier"]) + '</td>';
        }
    }

    document.getElementById("table_body").innerHTML += html;
    setEvents(fields);
}

// Hide a row
let hideRow = function(identifier) {
    let row = document.querySelector("tr[data-identifier='" + identifier + "']");
    row.style.display = "none";
};

// Delete a row
let deleteRow = function(fields, event) {
    let identifier = event.target.dataset.identifier;
    let row = document.querySelector("tr[data-identifier='" + identifier + "']");
    let data = {"identifier": identifier, "action": "delete"};

    handle_ajax("POST", fields["__url__"], data, (e) => {
        if (e.readyState == 4 && e.status == 200) {
            if (e.responseText == "true")
                hideRow(identifier);
            else if (e.responseText == "false")
                alert("Couldn't delete row.");
            else
                alert("Couldn't delete row - " + JSON.parse(e.responseText) + ".");
        }
    });
};

// Disable the modal editor
let disableModal = function() {
    document.getElementById("modal").classList = "modal fade";
};

// Enable the modal editor
let enableModal = function(fields, event, include, eventType, displayEvent, defaults={}) {
    let html = "<input type='hidden' name='action' value='" + eventType + "'>";
    Object.keys(fields).forEach((field) => {
        if (include == "*" || include.includes(field)) {
            let def = "";
            if (field in defaults)
                def = defaults[field];

            html += generateFormElement(field, fields, def, true);
        }
    });

    document.getElementById("modal_body").innerHTML = html;
    document.getElementById("modal").classList = "modal fade show";
    document.getElementById("modal_form").action = fields["__url__"];
    document.getElementById("modal_title").innerText = displayEvent;
    document.querySelectorAll("[data-action='submit_modal'")[0].innerText = displayEvent;
};

// Submit modal form
let submitModal = function(fields) {
    let modal_form = document.getElementById("modal_body");
    let data = {};

    for (let i = 0; i < modal_form.children.length; i++) {
        if (modal_form.children[i].nodeName != "LABEL") {
            field = modal_form.children[i].name;
            if (field in fields || field == "action") {
                let input = modal_form.children[i];
                if ("required" in input.attributes && input.value == "") {
                    data = false;
                    break;
                }
                else {
                    data[field] = input.value;

                    if (field == fields["__identifier__"]) {
                        data["identifier"] = input.value;
                    }
                }
            }
        }
    }

    if (data == false) {
        alert("All fields are required.");
    }
    else {
        handle_ajax("POST", fields["__url__"], data, (e) => {
            if (e.readyState == 4 && e.status == 200) {
                if (e.responseText == "true") {
                    disableModal(fields, data);
                    alert("Done.");

                    if (document.querySelector("[name='action']").value == "add") {
                        addRow(fields, data);
                    }
                    else if (document.querySelector("[name='action']").value == "choose_schema") {
                        let item = document.querySelector("tr[data-identifier='" + data["identifier"] + "'] \
                                                           [data-field='challenge_id']");
                        if (data["challenge_id"] == "__none__") {
                            item.innerHTML = "None";
                        }
                        else {
                            item.innerHTML = '<a href="' + data["challenge_id"] + '">View</a>';
                        }
                    }
                }
                else if (e.responseText == "false")
                    alert("Couldn't do that.");
                else
                    alert("Couldn't do that - " + JSON.parse(e.responseText) + ".");
            }
        });
    }
};


/* Event handling */
// A list of event handling functions
let fields;

let add_event = (event) => {
    enableModal(fields, event, "*", "add", "Add a new user");
};

let close_modal_event = (event) => {
    disableModal();
};

let submit_modal_event = (event) => {
    event.preventDefault();
    submitModal(fields);
};

let edit_event = (event) => {
    enableEditor(fields, event);
};

let delete_event = (event) => {
    deleteRow(fields, event);
};

let page_events_event = new Event("page_events");

// Set events for all the page's edit buttons
let setEvents = function(fs) {
    fields = fs;

    let edit_buttons = document.querySelectorAll("[data-action='edit']");
    edit_buttons.forEach(btn => {
        btn.removeEventListener("click", edit_event);
        btn.addEventListener("click", edit_event);
    });

    let delete_buttons = document.querySelectorAll("[data-action='delete']");
    delete_buttons.forEach(btn => {
        btn.removeEventListener("click", delete_event);
        btn.addEventListener("click", delete_event);
    });

    let add_buttons = document.querySelectorAll("[data-action='add']");
    add_buttons.forEach(btn => {
        btn.removeEventListener("click", add_event);
        btn.addEventListener("click", add_event);
    });

    let close_modal_buttons = document.querySelectorAll("[data-action='close_modal'");
    close_modal_buttons.forEach(btn => {
        btn.removeEventListener("click", close_modal_event);
        btn.addEventListener("click", close_modal_event);
    });

    let modal_form = document.getElementById("modal_form");
    if (modal_form != null) {
        modal_form.removeEventListener("submit", submit_modal_event);
        modal_form.addEventListener("submit", submit_modal_event);
    }

    document.dispatchEvent(page_events_event);

    // Disable # links
    let hash_links = document.querySelectorAll("a[href='#']");
    hash_links.forEach(link => {
        link.addEventListener("click", (event) => {
            event.preventDefault();
        });
    });
};
