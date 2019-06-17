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
function show_events(){
   var checkbox1 = document.getElementById("chk1");
   var checkbox2 = document.getElementById("chk2");
   var checkbox3 = document.getElementById("chk3");
   var hiddenInputs = document.getElementsByClassName("hidden");
   for(var i=0; i< hiddenInputs.length; i++)
   {
       if(checkbox1.checked || checkbox2.checked || checkbox3.checked)
       {
           hiddenInputs[i].style.display="inline";
       }
       else
       {
            hiddenInputs[i].style.display="none";
       }
   }
}
function show_test(){
    var testy = document.getElementById("testchk");
    var word = document.getElementsByClassName("test")
    for(var i=0; i<word.length; i++)
    {
        if (testy.checked)
        {
        word[i].style.display="inline";
        }
        else
        {
        word[i].style.display="none";
        }
    }

}
function object_changed(elem) {
    elem.form.submit()
}

function add_btn_pressed(story_id) {
    var template = document.getElementById("obj-template");
    var newelem = template.cloneNode(true);
    newelem.id = "";
    newelem.classList.add("object-main-row");
    newelem.childNodes[0].value = story_id;
    document.getElementById("main-site").insertBefore(newelem, document.getElementById("content-marker"));

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            // Successful Request
            var obj = JSON.parse(this.responseText);
            if (obj.status == "ok") {
                newelem.childNodes[1].value = obj.response.obj_id;
            } else {
                console.log("Bad Response, what do we do now?")
            }
        } else if (this.readyState == 4) {
            console.log("Bad Response, what do we do now?")
        }
    };
    xhttp.open("POST", "/story/object/new", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("desc=&name=&obj_start_location=0&story_id=" + story_id);
}

function delete_btn_pressed(story_id, obj_id) {
    var element = document.getElementByClassName("object-main-row");
    element.parentNode.removeChild(element);
    var element1 = document.getElementByID("obj-template");
    element.parentNode.removeChild(element1);
}