function editStory(story_id) {

}

function create_story_btn() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var json = JSON.parse(this.responseText);
            if (json.status == "ok") {
                window.location.href = "/story/update?story_id=" + json.story.story_id;
            } else {
                console.log(json);
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/story/new", true);
    xhttp.send();
}