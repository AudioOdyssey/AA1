function event_show(activ) {
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

function event_changed(elem) {
    elem.form.submit()
}

function add_btn_pressed(story_id) {
    var template = document.getElementById("ev-template");
    var newelem = template.cloneNode(true);
    newelem.id = "";
    newelem.classList.add("event-main-row");
    newelem.childNodes[0].value = story_id;
    document.getElementById("main-site").insertBefore(newelem, document.getElementById("content-marker"));

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Successful Request
            var event = JSON.parse(this.responseText);
            if (obj.status == "ok") {
                newelem.childNodes[1].value = ev.response.ev_id;
            } else {
                console.log("Bad Response, what do we do now?")
            }
        } else if (this.readyState == 4) {
            console.log("Bad Response, what do we do now?")
        }
    };
    xhttp.open("POST", "/story/event/new", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("desc=&name=&ev_start_location=0&story_id=" + story_id);
}