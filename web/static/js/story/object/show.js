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
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/object/update", true);
    // xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(new FormData(elem.form));
}

function add_btn_pressed(story_id) {
    var template = document.getElementById("obj-template");
    var newelem = template.cloneNode(true);
    newelem.id = "";
    newelem.classList.add("object-main-row");
    newelem.childNodes[0].value = story_id;
    document.getElementById("main-site").insertBefore(newelem, document.getElementById("content-marker"));

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            // Successful Request
            var obj = JSON.parse(this.responseText);
            if (obj.status == "ok") {
                newelem.childNodes[1].value = obj.response.obj_id;
            } else {
                console.log("Bad Response, what do we do now?");
                console.log(this.responseText);
            }
        } else if (this.readyState == 4) {
            console.log("Bad Response, what do we do now?")
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/object/new", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("desc=&name=&obj_start_location=0&story_id=" + story_id);
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