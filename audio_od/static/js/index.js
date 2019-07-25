var current_image = 0;

function left_image() {
    var elem = document.getElementById('hero-images');
    var oldid = current_image;

    if (current_image == 0)
        current_image = elem.childElementCount-1;
    else
        current_image--;

    // elem.style.right = 100 * current_image + "vw";
    transition_image(oldid);
}

function right_image() {
    var elem = document.getElementById('hero-images');
    var oldid = current_image;

    if (current_image == elem.childElementCount-1)
        current_image = 0;
    else
        current_image++;

    // elem.style.right = 100 * current_image + "vw";
    transition_image(oldid);
}

function transition_image(oldid) {
    var elem = document.getElementById('hero-images');
    var oldpos = oldid * 100;
    var newpos = current_image * 100;
    var count = 50;
    var timer = setInterval(function () {
        if (count == 0){
            clearInterval(timer);
            elem.style.right = newpos + "vw";
        }
        elem.style.right = (count/50.0 * oldpos + (50.0-count)/50.0 * newpos) + "vw";
        count--;
    }, 10);
}