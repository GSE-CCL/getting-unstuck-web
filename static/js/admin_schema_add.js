// Global editor variable
let editors = {
    "explanation": null,
    "concluding_text": null,
    "comparison_reflection_text": null,
    "comparison_framing_text": null,
    "prompt_framing_text": null,
    "stats_framing_text": null
};

// Add text option
let add_topt = (event) => {
    let max_id = parseInt(event.target.dataset.maxToId) + 1;

    let element = document.createElement("DIV");
    element.classList.add("input-group", "mt-2");
    element.dataset.toId = max_id;

    let parent_id = event.target.parentNode.dataset.trId;
    let opt_code = '<input type="text" class="form-control" placeholder="text option">'
                 +  '<div class="input-group-append">'
                 + '<button class="btn btn-outline-secondary" type="button" data-action="remove_parent" data-times="2">&times;</button></div></div>';

    event.target.dataset.maxToId = max_id;

    element.innerHTML = opt_code;

    event.target.parentNode.childNodes.forEach((child) => {
        if (child.classList && child.classList.contains("required_inner")) {
            child.appendChild(element);
        }
    });

    events_remove_parent();
};

// Add text requirement
let add_treq = (event) => {
    let max_id = parseInt(event.target.dataset.maxRtId) + 1;

    let element = document.createElement("DIV");
    element.classList.add("required_outer", "mt-2");
    element.dataset.trId = max_id;

    let req_code = '';
    if (max_id > 0) {
        req_code += '<small><em>and one of these</em></small>';
    }
    else {
        req_code += '<small><em>one of these</em></small>';
    }
    req_code += '<button class="btn btn-outline-secondary float-right mb-2" type="button" data-action="remove_parent" data-times="1" data-decrement="add_tr_btn;maxRtId">&times;</button>'
              + '<div><input type="radio" name="rt_comparison_basis" value="' + max_id + '" id="rt_comparison_basis_' + max_id + '"> '
              + '<label for="rt_comparison_basis_' + max_id + '">comparison basis</label></div>'
              + '<div class="required_inner"></div>'
              + '<button type="button" class="btn btn-secondary mt-2" data-action="add_to" data-max-to-id="-1">Add option</button>';

    event.target.dataset.maxRtId = max_id;

    element.innerHTML = req_code;

    let list = document.getElementById("required_text");
    list.appendChild(element);

    events_topt();
};

// Add block option
let add_bopt = (event) => {
    let max_id = parseInt(event.target.dataset.maxBoId) + 1;

    let element = document.createElement("DIV");
    element.classList.add("input-group", "mt-2");
    element.dataset.boId = max_id;

    let parent_id = event.target.parentNode.dataset.brId;
    let opt_code = '<input type="text" class="form-control block_input" placeholder="block requirement">'
                 + '<input type="number" class="form-control col-3" placeholder="min" required>'
                 + '<div class="form-control col-1 p-1 pt-2 text-center"><input type="radio" name="rb_comparison_basis_' + parent_id + '" value="' + max_id + '"></div>'
                 + '<div class="input-group-append">'
                 + '<button class="btn btn-outline-secondary" type="button" data-action="remove_parent" data-times="2">&times;</button></div>';

    event.target.dataset.maxBoId = max_id;

    element.innerHTML = opt_code;

    event.target.parentNode.childNodes.forEach((child) => {
        if (child.classList && child.classList.contains("required_inner")) {
            child.appendChild(element);
        }
    });

    events_remove_parent();
    events_block_choose();
};

// Add block requirement
let add_breq = (event) => {
    let max_id = parseInt(event.target.dataset.maxRbId) + 1;

    let element = document.createElement("DIV");
    element.classList.add("required_outer", "mt-2");
    element.dataset.brId = max_id;

    let req_code = '';
    if (max_id > 0) {
        req_code += '<small><em>or all of these</em></small>';
    }
    else {
        req_code += '<small><em>all of these</em></small>';
    }
    req_code += '<button class="btn btn-outline-secondary float-right mb-2" type="button" data-action="remove_parent" data-times="1" data-decrement="add_br_btn;maxRbId">&times;</button>'
              + '<div class="required_inner"></div>'
              + '<button type="button" class="btn btn-secondary mt-2" data-action="add_bo" data-max-bo-id="-1">Add requirement</button>';

    event.target.dataset.maxRbId = max_id;

    element.innerHTML = req_code;

    let list = document.getElementById("required_blocks");
    list.appendChild(element);

    events_bopt();
};

// Remove a parent
let remove_parent = (event) => {
    let ele = event.target;
    let oele = ele;

    let times = 1;
    if ("times" in ele.dataset) {
        times = ele.dataset.times;
    }

    for (let i = 0; i < times; i++) {
        ele = ele.parentNode;
    }

    ele.parentNode.removeChild(ele);

    // Decrementation functionality
    if ("decrement" in oele.dataset) {
        let decrement = oele.dataset.decrement;
        let parts = decrement.split(";");

        let dele = document.getElementById(parts[0]);
        let max = parseInt(dele.dataset[parts[1]]);
        dele.dataset[parts[1]] = max - 1;

        if (parts[0] == "add_tr_btn") {
            let el = document.querySelector("#required_text small:first-child em");
            if (el !== null) {
                el.innerText = "one of these";
            }
        }
        else if (parts[0] == "add_br_btn") {
            let el = document.querySelector("#required_blocks small:first-child em")
            if (el !== null) {
                el.innerText = "all of these";
            }
        }
    }
};

// Move and display block list
let move_blocks = (event) => {
    let obj = event.target.parentNode;
    let rect = obj.getBoundingClientRect();
    let helper = document.getElementById("block_input_helper");
    let scrollTop = (document.documentElement.scrollTop || document.body.scrollTop);

    helper.style.top = (rect.y + scrollTop + obj.clientHeight + 8) + "px";
    helper.style.left = rect.x + "px";
    helper.style.display = "block";
    helper.style.width = obj.clientWidth + "px";

    // Use object ID if available, otherwise try to use block requirement IDs
    if (event.target.id != undefined && event.target.id != "") {
        helper.dataset.tid = event.target.id;
    }
    else {
        helper.dataset.boId = obj.dataset.boId;
        helper.dataset.brId = obj.parentNode.parentNode.dataset.brId;
    }
    console.log(helper.dataset)
};

// Hide block list
let hide_blocks = (event=null) => {
    if (event == null
        || event.relatedTarget == null
        || !("action" in event.relatedTarget.dataset)
        || event.relatedTarget.dataset.action != "choose_block") {
        let helper = document.getElementById("block_input_helper");
        helper.style.display = "none";

        helper.dataset.boId = "";
        helper.dataset.brId = "";
        helper.dataset.tid = "";

        let list_items = document.querySelectorAll("#block_input_helper .list-group-item");
        list_items.forEach((list_item) => {
            list_item.style.display = "block";
        });
    }
};

// Suggest blocks based on text
let suggest_block = (event) => {
    let value = event.target.value;
    value = value.replace(/ /g, "");

    let display_categories = new Set();

    // Search
    block_list.forEach((block) => {
        if (block.includes(value)) {
            document.querySelector("[data-action='choose_block'][data-opcode='" + block + "']").style.display = "block";
            display_categories.add(block.split("_")[0]);
        }
        else {
            document.querySelector("[data-action='choose_block'][data-opcode='" + block + "']").style.display = "none";
            for (let key in block_dict) {
                if (key.includes(value)) {
                    document.querySelector("[data-action='choose_block'][data-opcode='" + block_dict[key] + "']").style.display = "block";
                    display_categories.add(block_dict[key].split("_")[0]);
                }
            }
        }
    });

    categories.forEach((category) => {
        if (!display_categories.has(category)) {
            document.querySelector("[data-block-category='" + category + "']").style.display = "none";
        }
        else {
            document.querySelector("[data-block-category='" + category + "']").style.display = "block";
        }
    });
};

// Choose a block opcode and put it into focused text box
let set_block = (event) => {
    let promise = new Promise((resolve) => {
        let opcode = event.target.dataset.opcode;
        if (event.target.nodeName == "STRONG")
            opcode = event.target.parentNode.dataset.opcode;

        let tid = document.getElementById("block_input_helper").dataset.tid;
        if (tid != undefined && tid != "") {
            document.getElementById(tid).value = opcode;
        }
        else {    
            let br_id = document.getElementById("block_input_helper").dataset.brId;
            let bo_id = document.getElementById("block_input_helper").dataset.boId;

            document.querySelector("[data-br-id='" + br_id + "'] [data-bo-id='" + bo_id + "'] input").value = opcode;
        }

        resolve();
    }).then(() => {
        hide_blocks();
    }).catch(() => {
        hide_blocks();
    });
};

// Grab nested values into a list
let get_nested = (id, adjacent_dict=false) => {
    let data = [];
    let requirements = document.querySelectorAll("#" + id + " .required_outer");
    requirements.forEach((req) => {
        let values = [];
        if (adjacent_dict) {
            values = {};
        }

        req.childNodes.forEach((c) => {
            if (c.classList && c.classList.contains("required_inner")) {
                c.childNodes.forEach((cr) => {
                    if (cr.classList && cr.classList.contains("input-group")) {
                        let v = [];
                        cr.childNodes.forEach((n) => {
                            if (n.nodeName == "INPUT" && n.value.replace(/ /g, "") != "") {
                                v.push(n.value);
                            }
                        });
                        if (adjacent_dict && v.length > 1) {
                            values[v[0]] = v[1];
                        }
                        else if (!adjacent_dict) {
                            values.push(v[0]);
                        }
                    }
                });
            }
        });
        
        if (values.length > 0 || (!Array.isArray(values) && Object.keys(values).length > 0)) {
            data.push(values);
        }
    });

    return data;
};

// Submit form
let submit_schema = (event) => {
    event.preventDefault();

    // Grab the data from the form
    let data = {
        id: event.target.dataset.schemaId,
        action: "edit",
        short_label: document.getElementById("short_label").value,
        title: document.getElementById("title").value,
        description: document.getElementById("description").value,
        url: {
            "url": document.getElementById("url").value,
            "text": document.getElementById("url_text").value
        },
        comparison_basis: {
            "basis": document.getElementById("comparison_basis").value,
            "priority": []
        },
        text: {},
        mins: {
            instructions_length: document.getElementById("min_instructions_length").value,
            description_length: document.getElementById("min_description_length").value,
            comments_made: document.getElementById("min_comments_made").value,
        },
        min_blockify: {
            comments: document.getElementById("min_blockify_comments").value,
            costumes: document.getElementById("min_blockify_costumes").value,
            sounds: document.getElementById("min_blockify_sounds").value,
            sprites: document.getElementById("min_blockify_sprites").value,
            variables: document.getElementById("min_blockify_variables").value
        },
        required_block_categories: {},
        required_blocks: get_nested("required_blocks", true),
        required_text: get_nested("required_text"),
        required_text_failure: document.getElementById("required_text_failure").value,
        required_blocks_failure: document.getElementById("required_blocks_failure").value,
        stats: []
    };

    let promise = new Promise((resolve) => {
        // Grab minimum of each category
        categories.forEach((category) => {
            data["required_block_categories"][category] = parseInt(document.getElementById("min_categories_" + category).value);
        });

        // Markdown editors
        Object.keys(editors).forEach((eid) => {
            data["text"][eid] = editors[eid].getValue();
        });

        // Get the priorities for what to show
        if (data["comparison_basis"]["basis"] == "required_text") {
            data["comparison_basis"]["priority"] = parseInt(get_radio(document.getElementsByName("rt_comparison_basis")))
        }
        else if (data["comparison_basis"]["basis"] == "required_block_categories") {
            data["comparison_basis"]["priority"] = get_radio(document.getElementsByName("rc_comparison_basis"));
        }
        else if (data["comparison_basis"]["basis"] == "required_blocks") {
            for (let i = 0; i < data["required_blocks"].length; i++) {
                let index = parseInt(get_radio(document.getElementsByName("rb_comparison_basis_" + i)));
                data["comparison_basis"]["priority"].push(
                    document.querySelector("[data-br-id='" + i + "'] [data-bo-id='" + index + "'] .block_input").value
                );
            }
        }

        // Get the studio stats to show
        for (let i = 0; i < 5; i++) {
            let stat = document.getElementById("studio_stats_" + i).value;

            if (stat.indexOf("/blocks") > -1) {
                let block = document.getElementById("studio_stats_block_" + i).value;

                if (block == "" || block == undefined) {
                    throw "Must choose a block for studio stat number " + (i + 1) + ".";
                }

                data["stats"].push(stat + "/" + block);
            }
            else if (stat.indexOf("/block_categories") > -1) {
                let cat = document.getElementById("studio_stats_category_" + i).value;

                if (cat == "" || cat == undefined) {
                    throw "Must choose a category for studio stat number " + (i + 1) + ".";
                }

                data["stats"].push(stat + "/" + cat);
            }
            else if (stat != "__none__") {
                data["stats"].push(stat);
            }
        }

        resolve();
    }).then(() => {
        // Submit form
        handle_ajax("POST", "/admin/schemas", data, (result) => {
            if (result.response == "true") {
                window.location = "/admin/schemas";
            }
            else {
                alert("Couldn't save the schema.")
            }
        }, "json");
    }).catch((err) => {
        if (err != "") {
            alert(err);
        }
        else {
            alert("Couldn't save schema.");
        }
    });    
};

// Disable the modal
let disableModal = function() {
    document.getElementById("modal").classList = "modal fade";
};

// Preview Markdown
let preview_markdown = (e) => {
    let editor = e.target.dataset.editor;
    let data = {"text": editors[editor].getValue()};
    handle_ajax("POST", "/md", data, (result) => {
        if (result.response == "False") {
            alert("Couldn't load preview.");
        }
        else {
            res = JSON.parse(result.response);
            document.getElementById("modal_title").innerText = "Markdown preview";
            document.getElementById("modal_body").innerHTML = res["html"];
            document.getElementById("modal").classList = "modal fade show";
            add_js(res["js"]);
        }
    });
};

// Show more detailed options for studio stats as needed
let handle_stats = (event) => {
    let id = event.target.dataset.statId;
    if (event.target.value.indexOf("/blocks") > -1) {
        document.getElementById("studio_stats_block_" + id).classList.remove("d-none");
        document.getElementById("studio_stats_category_" + id).classList.add("d-none");
    }
    else if (event.target.value.indexOf("/block_categories") > -1) {
        document.getElementById("studio_stats_category_" + id).classList.remove("d-none");
        document.getElementById("studio_stats_block_" + id).classList.add("d-none");
    }
    else {
        document.getElementById("studio_stats_block_" + id).classList.add("d-none");
        document.getElementById("studio_stats_category_" + id).classList.add("d-none");
    }
};

// Event setters
let events_topt = () => {
    let add_tos = document.querySelectorAll("[data-action='add_to']");
    add_tos.forEach((add_to) => {
        add_to.addEventListener("click", add_topt);
    });
    events_remove_parent();
};

let events_bopt = () => {
    let add_bos = document.querySelectorAll("[data-action='add_bo']");
    add_bos.forEach((add_bo) => {
        add_bo.addEventListener("click", add_bopt);
    });
    events_remove_parent();
};

let events_remove_parent = () => {
    let rps = document.querySelectorAll("[data-action='remove_parent']");
    rps.forEach((rp) => {
        rp.removeEventListener("click", remove_parent);
        rp.addEventListener("click", remove_parent);
    });
};

let events_block_choose = () => {
    let block_inputs = document.querySelectorAll(".block_input");
    block_inputs.forEach((block_input) => {
        block_input.removeEventListener("keyup", suggest_block);
        block_input.addEventListener("keyup", suggest_block);

        block_input.removeEventListener("focus", move_blocks);
        block_input.addEventListener("focus", move_blocks);

        block_input.removeEventListener("blur", hide_blocks);
        block_input.addEventListener("blur", hide_blocks);
    });
};

let events_block_selector = () => {
    let buttons = document.querySelectorAll("[data-action='choose_block']");
    buttons.forEach((button) => {
        button.addEventListener("click", set_block);
    });
};

let events_studio_stats = () => {
    let inputs = document.querySelectorAll(".studio_stats");
    inputs.forEach((input) => {
        input.addEventListener("change", handle_stats);
    });
}

let loaded = function() {
    // Required text
    events_topt();
    let add_rts = document.querySelectorAll("[data-action='add_tr']");
    add_rts.forEach((add_tr) => {
        add_tr.addEventListener("click", add_treq);
    });

    // Required blocks
    events_bopt();
    let add_bts = document.querySelectorAll("[data-action='add_br']");
    add_bts.forEach((add_br) => {
        add_br.addEventListener("click", add_breq);
    });

    // Block selector
    events_block_selector();
    events_block_choose();

    // Studio stats
    events_studio_stats();

    // Form submission
    document.getElementById("schema_form").addEventListener("submit", submit_schema);

    // Markdown editors
    ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11/");
    Object.keys(editors).forEach((eid) => {
        editors[eid] = ace.edit(eid, {
            maxLines: 30,
            theme: "ace/theme/clouds"
        });

        editors[eid].setHighlightActiveLine(false);
        editors[eid].session.setUseWrapMode(true);
        editors[eid].session.setMode("ace/mode/markdown");
        editors[eid].on("change", () => {
            editors[eid].resize(true);
        });
    })
    
    let preview_btns = document.querySelectorAll("[data-action='preview_markdown']")
    preview_btns.forEach((btn) => {
        btn.addEventListener("click", preview_markdown);
    });

    let modal_close_btns = document.querySelectorAll("[data-action='close_modal']");
    modal_close_btns.forEach((mcb) => {
        mcb.addEventListener("click", disableModal);
    });
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
