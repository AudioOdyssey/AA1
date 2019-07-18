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

function loadpage(url) {
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