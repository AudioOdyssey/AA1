function save() {
    // story_changed(document.getElementById("edit-story-details"));
    document.getElementById("save-bubble").style.opacity = 1;
    document.getElementById("save-bubble").style.filter = 'alpha(opacity=100)';
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