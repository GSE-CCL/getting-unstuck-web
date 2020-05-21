// Add text option
let add_topt = (event) => {
    let max_id = parseInt(event.target.dataset.maxToId) + 1;
    let opt_code = '<div data-to-id="' + max_id + '" class="input-group mt-2"> \
    <input type="text" class="form-control" placeholder="text option"> \
    <div class="input-group-append"> \
    <button class="btn btn-outline-secondary" type="button" data-action="remove_parent" data-times="2">&times;</button></div></div>';``

    event.target.dataset.maxToId = max_id;

    let list = event.target.parentNode.childNodes[3];
    list.innerHTML += opt_code;

    events_remove_parent();
};

// Add text requirement
let add_treq = (event) => {
    let max_id = parseInt(event.target.dataset.maxRtId) + 1;

    let req_code = '<div class="required_outer mt-2" data-tr-id="' + max_id + '">';
    if (max_id > 0) {
        req_code += '<small><em>and one of these</em></small>';
    }
    else {
        req_code += '<small><em>one of these</em></small>';
    }
    req_code += '<button class="btn btn-outline-secondary float-right mb-2" type="button" data-action="remove_parent" data-times="1" data-decrement="add_tr_btn;maxRtId">&times;</button> \
        <div class="required_inner"></div> \
        <button type="button" class="btn btn-secondary mt-2" data-action="add_to" data-max-to-id="-1">Add option</button></div>';

    event.target.dataset.maxRtId = max_id;

    let list = document.getElementById("required_text");
    list.innerHTML += req_code;

    events_topt();
};

// Add block option
let add_bopt = (event) => {
    let max_id = parseInt(event.target.dataset.maxBoId) + 1;
    let opt_code = '<div data-bo-id="' + max_id + '" class="input-group mt-2"> \
        <input type="text" class="form-control" placeholder="block requirement"> \
        <div class="input-group-append"> \
        <button class="btn btn-outline-secondary" type="button" data-action="remove_parent" data-times="2">&times;</button></div></div>';

    event.target.dataset.maxBoId = max_id;

    let list = event.target.parentNode.childNodes[3];
    list.innerHTML += opt_code;

    events_remove_parent();
};

// Add block requirement
let add_breq = (event) => {
    let max_id = parseInt(event.target.dataset.maxRbId) + 1;

    let req_code = '<div class="required_outer mt-2" data-br-id="' + max_id + '">';
    if (max_id > 0) {
        req_code += '<small><em>or all of these</em></small>';
    }
    else {
        req_code += '<small><em>all of these</em></small>';
    }
    req_code += '<button class="btn btn-outline-secondary float-right mb-2" type="button" data-action="remove_parent" data-times="1" data-decrement="add_br_btn;maxRbId">&times;</button> \
        <div class="required_inner"></div> \
        <button type="button" class="btn btn-secondary mt-2" data-action="add_bo" data-max-bo-id="-1">Add requirement</button></div>';

    event.target.dataset.maxRbId = max_id;

    let list = document.getElementById("required_blocks");
    list.innerHTML += req_code;

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
};

if (document.readyState === "complete")
    loaded();
else
    document.addEventListener("DOMContentLoaded", loaded);
