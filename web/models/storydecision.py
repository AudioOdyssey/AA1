class StoryDecision:
    story_id = 0
    loc_id = 0
    sequence_num = 0
    decision_id = 0
    decision_name = ""
    transition = True
    transition_loc_id = 0
    hidden = False
    locked = False
    decision_description = ""
    show_event_id = 0
    show_object_id = 0
    locked_event_id = 0 
    unlock_event_id = 0
    locked_descr = ""
    aftermath_descr = ""
    cause_event = False
    effect_event_id = 0

    def __init__(self):
        pass