function show(activ) {
    var elem = activ.parentNode.nextElementSibling
    if (elem.style.display == "block")
        elem.style.display = "none";
    else
        elem.style.display = "block";
}
function verify_changed(elem) {
    // elem.form.submit()
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/verification/review/update", true);
    // xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send(new FormData(elem.form));
}

function set_focus(elem) {
        try {
            document.getElementById("active").id = "";
        } catch (err) {
    
        }
        elem.id = "active";
}
function verify_story(story_id) {

}

