function decision_show(activ) {
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

function checkbox_visability_check(elem) { //does not work
    if (elem.checked)
        elem.parentNode.getElementsByClassName("checkbox_hide")[0].style.display = "block";
    else
        elem.parentNode.getElementsByClassName("checkbox_hide")[0].style.display = "none";
}

function decision_changed(elem) {
    // elem.form.submit()

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
            save();
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/location/decision/update", true);
    // xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(new FormData(elem.form));
}

function check_exclusivity(elem) {
    if (elem.options[elem.selectedIndex].value !== 0) {
        elems = elem.parentNode.parentNode.getElementsByClassName("exclusive")
        for (var i = 0; i < elems.length; i++) {
            if (elems[i] != elem && elems[i].selectedIndex != 0) {
                elems[i].selectedIndex = 0;
            }
        }
    }
}

function add_btn_pressed_dec(story_id, location_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") { 
                window.location.href = "/story/location/decision/indiv?story_id=" + story_id + "&location_id=" + location_id + "&decision_id=" + json.decision.decision_id;
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/location/decision/new?story_id=" + story_id + "&location_id=" + location_id, true);
    xhttp.send();
}

function add_btn_pressed_obj(story_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                window.location.href = "/story/object/indiv?story_id=" + story_id + "&object_id=" + json.object.obj_id;
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/object/new?story_id=" + story_id, true);
    xhttp.send();
}
function delete_btn_pressed(btn) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/location/decision/destroy", true);
    xhttp.send(new FormData(btn.form));
    btn.parentNode.parentNode.removeChild(btn.parentNode);
}



function add_btn_pressed_loc(story_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                window.location.href = "/story/location/indiv?story_id=" + story_id + "&location_id=" + json.location.location_id;
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/location/new?story_id=" + story_id, true);
    xhttp.send();
}

function add_btn_pressed_evt(story_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                window.location.href = "/story/event/indiv?story_id=" + story_id + "&event_id=" + json.event.event_id;
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/event/new?story_id=" + story_id, true);
    xhttp.send();
}