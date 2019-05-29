function object_show(activ) {
    var elem = activ.parentNode.nextElementSibling
    if (elem.style.display == "block")
        elem.style.display = "none";
    else
        elem.style.display = "block";
}

function set_focus(elem) {
    try {
        document.getElementById("active").id = "";
    } catch (err) {

    }
    elem.id = "active";
}

function object_changed(elem) {
    elem.form.submit()
}

function add_btn_pressed() {
    var template = document.getElementById("obj-template");
    var newelem = template.cloneNode(true);
}