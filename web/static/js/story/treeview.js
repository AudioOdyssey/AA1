function get_starting_loc(story_id, elem)
{
    window.location.href = "/story/treeview?story_id=" + story_id + "&location_id=" + elem.options[elem.selectedIndex].value;
}