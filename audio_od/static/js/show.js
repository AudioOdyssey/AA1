function show_show(activ) {
    var elem = activ.parentNode.nextElementSibling
    if (elem.style.display == "block")
        elem.style.display = "none";
    else
        elem.style.display = "block";
}

function show_set_focus(elem) {
    try {
        document.getElementById("show-active").id = "";
    } catch (err) {

    }
    elem.id = "show-active";
}

function show_checkbox_visability_check(elem) {
    if (elem.checked)
        elem.parentNode.getElementsByClassName("checkbox_hide")[0].style.display = "block";
    else
        elem.parentNode.getElementsByClassName("checkbox_hide")[0].style.display = "none";
}

function show_changed(elem, endpt) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
            save();
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/" + endpt + "/update", true);
    xhttp.send(new FormData(elem.form));
}

function add_obj_redir(story_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                loadpage("/story/object/indiv?story_id=" + story_id + "&object_id=" + json.object.obj_id);
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/object/new?story_id="+story_id, true);
    xhttp.send();
}

function add_evt_redir(story_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                loadpage("/story/event/indiv?story_id=" + story_id + "&event_id=" + json.event.event_id);
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/event/new?story_id="+story_id, true);
    xhttp.send();
}

function add_loc_redir(story_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                loadpage("/story/location/indiv?story_id=" + story_id + "&location_id=" + json.location.location_id);
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/location/new?story_id="+story_id, true);
    xhttp.send();
}

function add_dec_redir(story_id, location_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") { 
                loadpage("/story/location/decision/indiv?story_id=" + story_id + "&location_id=" + location_id + "&decision_id=" + json.decision.decision_id);
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

function show_delete_pressed(btn, endpt) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            btn.parentNode.parentNode.removeChild(btn.parentNode);
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/" + endpt + "/destroy", true);
    xhttp.send(new FormData(btn.form));
}

function show_check_exclusivity(elem) {
    if (elem.options[elem.selectedIndex].value !== 0) {
        elems = elem.parentNode.parentNode.getElementsByClassName("exclusive")
        for (var i = 0; i < elems.length; i++) {
            if (elems[i] != elem && elems[i].selectedIndex != 0) {
                elems[i].selectedIndex = 0;
            }
        }
    }
}

function tree_go_starting_loc(endpoint, story_id, elem) {
    loadpage(endpoint + "?story_id=" + story_id + "&location_id=" + elem.options[elem.selectedIndex].value);
}