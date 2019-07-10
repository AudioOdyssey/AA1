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

function handleFileSelect(evt) {
    var files = evt.target.files;
    var f = files[0];
    var reader = new FileReader();

    reader.onload = (function (theFile) {
        return function (e) {
            document.getElementById('cover-photo').style.backgroundImage = "url('" + e.target.result + "')";
        };
    })(f);

    reader.readAsDataURL(f);
}

function save() {
    story_changed(document.getElementById("edit-story-details"));
    document.getElementById("save-bubble").style.display = "block";
    window.setTimeout(savedone,1500);
}

function savedone() {
    var element = document.getElementById("save-bubble");
    var op = 1;
    var timer = setInterval(function () {
        if (op <= 0.1){
            clearInterval(timer);
            element.style.display = 'none';
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op -= op * 0.1;
    }, 25);
}