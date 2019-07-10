function transferFailed(e) {
    console.log("Error");
}

function story_changed(elem) {
    var xhttp = new XMLHttpRequest();
    xhttp.addEventListener("abort", transferFailed);
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log("200");
        } else if (this.readyState == 4) {
            console.log(this.status);
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/update", true);
    xhttp.send(new FormData(elem.form));
}

function story_delete(story_id) {
    if (!confirm("You are sure you want to delete this story?"))
        return;
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/destroy", true);
    xhttp.send("story_id=" + story_id);
}

function add_btn_obj(story_id) {
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

function add_btn_evt(story_id) {
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

function add_btn_loc(story_id) {
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

function publish_story(story_id) //TODO ??
{

}