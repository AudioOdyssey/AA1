loadprofile();

function loadprofile() {
	var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
        	if (this.responseText != '')
            	document.getElementById("sidebar-profile").style.backgroundImage = 
            		"url(data:image/png;base64," + this.responseText + ")";
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("GET", "/user/picture", true);
    xhttp.send();
}

window.onpopstate = function (e) {
    bareloadpage(event.state.page)
}

function bareloadpage(url) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            if (this.responseText != '')
                document.getElementById("dash-content").innerHTML = this.responseText;
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function loadpage(url) {
	var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
        	if (this.responseText != '') {
                let stateObj = {
                    page: url,
                };

                history.pushState(stateObj, "", "/dashboard"+url);
            	document.getElementById("dash-content").innerHTML = this.responseText;
            }
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function user_changed(elem) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            save();
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/user/update", true);
    xhttp.send(new FormData(elem.form));
}

function profile_changed(evt, elem) {
    var files = evt.target.files;
    var f = files[0];
    var filesize = ((f.size / 1024) / 1024).toFixed(4);
    if (filesize > 7.9) {
        // The image is DUMMY THICC and the clap alerted the server!
        document.getElementById("dummy-thicc").style.display = "block";
        return;
    }
    document.getElementById("dummy-thicc").style.display = "none";
    
    var reader = new FileReader();

    reader.onload = (function (theFile) {
        return function (e) {
            var elems = document.getElementsByClassName('user-image')
            for (var i = 0; i < elems.length; i++)
                elems[i].style.backgroundImage = "url('" + e.target.result + "')";
        };
    })(f);

    reader.readAsDataURL(f);

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            save();
        } else if (this.readyState == 4) {
            console.log(this.responseText);
        }
    };
    xhttp.open("POST", "/user/picture", true);
    xhttp.send(new FormData(elem.form));
}