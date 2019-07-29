function runSetCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function runGetCookie(cname) {
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

function runAddItem(item) {
    var items = runGetCookie("rundata");
    if (items == "")
        items = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(items);
    if (obj.items.indexOf(item) === -1) obj.items.push(item);
    var cookie = JSON.stringify(obj);
    runSetCookie("rundata", cookie, 1);
}

function runAddEvent(event) {
    var events = runGetCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    if (obj.events.indexOf(event) === -1) obj.events.push(event);
    var cookie = JSON.stringify(obj);
    runSetCookie("rundata", cookie, 1);
}

function runAddDec(dec) {
    var events = runGetCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    if (obj.decs.indexOf(dec) === -1) obj.decs.push(dec);
    var cookie = JSON.stringify(obj);
    runSetCookie("rundata", cookie, 1);
}

function runAddBack(back) {
    var events = runGetCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    obj.back.push(back);
    var cookie = JSON.stringify(obj);
    runSetCookie("rundata", cookie, 1);
}

function runDecDone(dec) {
    var events = runGetCookie("rundata");
    if (events == "")
        events = '{"items":[], "events":[], "decs":[], "back":[]}'
    var obj = JSON.parse(events);
    return obj.events.indexOf(dec) === -1
}

function runPopLoc() {
    var events = runGetCookie("rundata");
    if (events == "")
        return "";
    var obj = JSON.parse(events);
    var ret = obj.back.pop();
    var cookie = JSON.stringify(obj);
    runSetCookie("rundata", cookie, 1);
    return ret;
}

function runDecClicked(story_id, dec_id, loc_id, transition, transition_loc_id, can_occur_once, cause_event, effect_event_id) {
    if (cause_event == 1 && effect_event_id != 0)
        runAddEvent(effect_event_id);
    if (can_occur_once == 1 && !runDecDone())
        runAddDec(dec_id);
    if (transition == 1) {
        runAddBack(loc_id);
        loadpage("/story/run?story_id=" + story_id + "&location_id=" + transition_loc_id);
    }
}

function runStartOver(story_id) {
    runSetCookie("rundata", "", -1); // Delete Cookie
    loadpage("/story/run?story_id=" + story_id);
}

function runBackOne(story_id) {
    var id = runPopLoc();
    loadpage("/story/run?story_id=" + story_id + "&location_id=" + id);
}