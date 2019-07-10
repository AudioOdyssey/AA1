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
        items = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(items);
    if (obj.items.indexOf(item) === -1) obj.items.push(item);
    var cookie = JSON.stringify(obj);
    setCookie("rundata", cookie, 1);
}

function addEvent(event) {
    var events = getCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    if (obj.events.indexOf(item) === -1) obj.events.push(item);
    var cookie = JSON.stringify(obj);
    setCookie("rundata", cookie, 1);
}

function addDec(dec) {
    var events = getCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    if (obj.decs.indexOf(dec) === -1) obj.decs.push(dec);
    var cookie = JSON.stringify(obj);
    setCookie("rundata", cookie, 1);
}

function addBack(back) {
    var events = getCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    obj.back.push(back);
    var cookie = JSON.stringify(obj);
    setCookie("rundata", cookie, 1);
}

function decDone(dec) {
    var events = getCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    return obj.events.indexOf(item) === -1
}

function dec_clicked(story_id, dec_id, transition, transition_loc_id, can_occur_once, cause_event, effect_event_id) {
    if (cause_event)
        addEvent(effect_event_id);
    if (can_occur_once && !decDone())
        addDec(dec_id);
    if (transition)
        addBack(transition_loc_id);
        window.location.href = "/story/run?story_id=" + story_id + "&location_id=" + transition_loc_id
}