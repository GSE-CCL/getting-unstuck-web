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
        "__identifer__": "username"
    };

    Here, username, email, and role are all fields in the table.
    Their type attributes represent their form types as
    should be displayed. For the role field, it's a select
    type, so options are provided as an array.

    __url__ is the POST URL for the form.
    
    __identifier__ tells us which field is the unique one in the table.
    Your table should have a data-identifier attribute on each row,
    and each edit button should have data-identifer and data-action "edit".
**/

// Disable the row editor
let disableEditor = function(fields, data) {
    let identifier = data[fields["__identifer__"]];
    let row = document.querySelector("tr[data-identifier='" + data["identifier"] + "']");
    row.dataset.identifier = identifier;

    for (let i = 0; i < row.children.length; i++) {
        field = row.children[i].dataset.field;
        if (field in fields) {
            row.children[i].innerText = data[field];
        }
        else if (field == "actions") {
            let html = '<a href="#" data-action="edit" data-identifier="' + identifier + '">Edit</a>';
            row.children[i].innerHTML = html;
            setEvents(fields);
        }
    }
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

            if (fields[field]["type"] == "text"
                || fields[field]["type"] == "email"
                || fields[field]["type"] == "password") {
                row.children[i].innerHTML = '<input type="' + fields[field]["type"]
                                            + '" required class="form-control" name="'
                                            + field + '" value="' + row.children[i].innerText + '">';
            }
            else if (fields[field]["type"] == "select") {
                let html = '<select name="' + field + '" class="form-control">';
                fields[field]["options"].forEach(option => {
                    html += '<option value="' + option + '"';

                    if (option == row.children[i].innerText)
                        html += " selected";

                    html += '>' + option + '</option>';
                });
                html += '</select>';

                row.children[i].innerHTML = html;
            }
        }
        else if (field == "actions") {
            row.children[i].innerHTML = '<button class="btn btn-primary" data-action="save" data-identifier="'
                                        + identifier +'">Save</button>'
                                        + '<a href="#" data-action="cancel" data-identifier="' + identifier + '">Cancel</a>';
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
    let data = {"identifier": identifier, "action": "edit"}

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
        datas = new URLSearchParams(data)

        var http = new XMLHttpRequest();
        http.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                if (this.responseText == "true")
                    disableEditor(fields, data);
            }
        };
        http.open("POST", fields["__url__"], true);
        http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        http.send(datas.toString());
    }
};

// Set events for all the page's edit buttons
let setEvents = function(fields) {
    let edit_event = (event) => {
        enableEditor(fields, event);
    };

    let edit_buttons = document.querySelectorAll("[data-action='edit']")
    edit_buttons.forEach(btn => {
        btn.removeEventListener("click", edit_event);
        btn.addEventListener("click", edit_event);
    });
};
