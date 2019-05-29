function object_show(obj_id) {
    var elem = document.getElementById("object_id" + obj_id);
    if (elem.style.display == "block")
        elem.style.display = "none";
    else
        elem.style.display = "block";
}

function set_focus(obj_id) {
    var elem = document.getElementById("object_id" + obj_id);
    try {
        document.getElementById("active").id = "";
    } catch (err) {

    }
    elem.parentElement.id = "active";
}

function object_changed(obj_id) {
    var elem = document.getElementById("object_id" + obj_id);
    elem.parentElement.submit()
}

function add_btn_pressed() {
    var template = document.getElementById("obj-template");
    var newelem = template.cloneNode(true);
}