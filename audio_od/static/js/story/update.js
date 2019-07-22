function story_changed(elem) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            save();
        } else if (this.readyState == 4) {
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
            window.location.href = "/story/show"
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/destroy?story_id=" + story_id, true);
    xhttp.send();
}

function storyHandleFileSelect(evt) {
    var files = evt.target.files;
    var f = files[0];
    var filesize = ((f.size / 1024) / 1024).toFixed(4);
    if (filesize > 7.5) {
        // The image is DUMMY THICC and the clap alerted the server!
        document.getElementById("dummy-thicc").style.display = "block";
        return;
    }
    var reader = new FileReader();

    reader.onload = (function (theFile) {
        return function (e) {
            document.getElementById('cover-photo').style.backgroundImage = "url('" + e.target.result + "')";
        };
    })(f);

    reader.readAsDataURL(f);
}

function storySubmitForVerify(uid) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                window.location.href = "/story/show";
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/verification/submit?story_id=" + uid, true);
    xhttp.send();
}

function storyLoadCover(sid) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("cover-photo").style.backgroundImage =
                "url(data:image/png;base64," + this.responseText + ")";
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("GET", "/story/image?story_id=" + sid, true);
    xhttp.send();

    document.getElementById('cover-upload').addEventListener('change', storyHandleFileSelect, false);
}