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

function decision_changed(elem) {
    elem.form.submit()
}

function add_btn_pressed(story_id, location_id) {
    var template = document.getElementById("dec-template");
    var newelem = template.cloneNode(true);
    newelem.id = "";
    newelem.classList.add("decision-main-row");
    newelem.childNodes[0].value = story_id;
    document.getElementById("main-site").insertBefore(newelem, document.getElementById("content-marker"));

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Successful Request
            var obj = JSON.parse(this.responseText);
            if (obj.status == "ok") {
                newelem.childNodes[1].value = obj.response.decision_id;
            } else {
                console.log("Bad Response, what do we do now?")
            }
        } else if (this.readyState == 4) {
            console.log("Bad Response, what do we do now?")
        }
    };
    xhttp.open("POST", "/story/location/decision/new", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("decision_name=&loc_id=" + location_id + "&story_id=" + story_id);
}
function delete_btn_pressed(story_id, decision_id) {
   
}