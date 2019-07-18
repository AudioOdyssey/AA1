function object_show(activ) {
    var elem = activ.parentNode.nextElementSibling
    if (elem.style.display == "block")
        elem.style.display = "none";
    else
        elem.style.display = "block";
}

function set_focus(elem) {
    try {
        document.getElementById("show-active").id = "";
    } catch (err) {

    }
    elem.id = "show-active";
}

function checkbox_visability_check(elem) {
    if (elem.checked)
        elem.parentNode.getElementsByClassName("checkbox_hide")[0].style.display = "block";
    else
        elem.parentNode.getElementsByClassName("checkbox_hide")[0].style.display = "none";
}

function object_changed(elem) {
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
    xhttp.open("POST", "/story/object/update", true);
    // xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(new FormData(elem.form));
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
    xhttp.open("POST", "/story/object/new?story_id="+story_id, true);
    xhttp.send();
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
    xhttp.open("POST", "/story/location/new?story_id="+story_id, true);
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
    xhttp.open("POST", "/story/object/destroy", true);
    xhttp.send(new FormData(btn.form));
    btn.parentNode.parentNode.removeChild(btn.parentNode);
}
function namegiven(elem) //TODO FIX THIS FUNCTION AND ADD IT TO THE OTHER FORMS SO WE CAN REQUIRE NAMES
{
    if (elem.value !== "")
    {
        getElementById("down").style.display="inline";
    }
}