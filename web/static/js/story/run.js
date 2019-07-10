function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function addItem(item) {
    var items = getCookie("rundata");
    if (items == "")
        items = '{"items":[], "events":[]}'
    var obj = JSON.parse(items);
    if (obj.items.indexOf(item) === -1) obj.items.push(item);
    var cookie = JSON.stringify(obj);
    setCookie("rundata", cookie, 1);
}

function addEvent(event) {
    var events = getCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[]}'
    var obj = JSON.parse(events);
    if (obj.events.indexOf(item) === -1) obj.events.push(item);
    var cookie = JSON.stringify(obj);
    setCookie("rundata", cookie, 1);
}