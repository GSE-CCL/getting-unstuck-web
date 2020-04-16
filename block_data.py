# Dictionary of Block Names (name, label, and category)

blocknames = [{"name": "motion_movesteps", "label": "Move Steps", "category": "motion"}, {"name": "motion_turnright", "label": "Turn Right", "category": "motion"}, {"name": "motion_turnleft", "label": "Turn Left", "category": "motion"},
    {"name": "motion_goto", "label": "Go to", "category": "motion"}, {"name": "motion_goto_menu", "label": "Go to Menu", "category": "motion"}, {"name": "motion_gotoxy", "label": "Go to XY", "category": "motion"},
    {"name": "motion_glideto", "label": "Glide To", "category": "motion"}, {"name": "motion_glidesecstoxy", "label": "Glide Secs to XY", "category": "motion"}, {"name": "motion_pointindirection", "label": "Point in Direction", "category": "motion"},
    {"name": "motion_pointtowards_menu", "label": "Point Towards Menu", "category": "motion"}, {"name": "motion_pointtowards", "label": "Point Towards", "category": "motion"},
    {"name": "motion_changexby", "label": "Change X By", "category": "motion"}, {"name": "motion_setx", "label": "Set X", "category": "motion"}, {"name": "motion_changeyby", "label": "Change Y By", "category": "motion"},
    {"name": "motion_sety", "label": "Set Y", "category": "motion"}, {"name": "motion_ifonedgebounce", "label": "If on Edge, Bounce", "category": "motion"}, {"name": "motion_setrotationstyle", "label": "Set Rotation Style", "category": "motion"},
    {"name": "motion_xposition", "label": "X Position", "category": "motion"}, {"name": "motion_yposition", "label": "Y Position", "category": "motion"},
    {"name": "motion_direction", "label": "Direction", "category": "motion"}, {"name": "control_wait", "label": "Wait Seconds", "category": "control"}, {"name": "control_repeat", "label": "Repeat", "category": "control"},
    {"name": "control_if", "label": "If", "category": "control"}, {"name": "control_forever", "label": "Forever", "category": "control"},
    {"name": "control_repeat_until", "label": "Repeat Until", "category": "control"}, {"name": "control_stop", "label": "Stop", "category": "control"},
    {"name": "control_start_as_clone", "label": "Start as Clone", "category": "control"}, {"name": "control_create_clone_of", "label": "Create Clone of", "category": "control"},
    {"name": "control_create_clone_of_menu", "label": "Create Clone of", "category": "control"}, {"name": "control_delete_this_clone", "label": "Delete this Clone", "category": "control"},
    {"name": "control_if_else", "label": "If Else", "category": "control"}, {"name": "control_wait_until", "label": "Wait Until", "category": "control"},
    {"name": "event_whenflagclicked", "label": "When Flag Clicked", "category": "event"}, {"name": "event_whenkeypressed", "label": "When Key Pressed", "category": "event"},
    {"name": "event_whenthisspriteclicked", "label": "When Sprite Clicked", "category": "event"}, {"name": "event_whenflagclicked", "label": "When Flag Clicked", "category": "event"},
    {"name": "event_whenbackdropswitchesto", "label": "When Backdrop Switches to", "category": "event"}, {"name": "event_whengreaterthan", "label": "When Greater Than", "category": "event"},
    {"name": "event_whenbroadcastreceived", "label": "When Broadcast Received", "category": "event"}, {"name": "event_broadcast", "label": "Broadcast", "category": "event"},
    {"name": "event_broadcastandwait", "label": "Broadcast Event and Wait", "category": "event"},
    {"name": "looks_sayforsecs", "label": "Say for Secs", "category": "looks"}, {"name": "looks_say", "label": "Say", "category": "looks"},
    {"name": "looks_switchcostumeto", "label": "Switch Costume", "category": "looks"}, {"name": "looks_costume", "label": "Costume", "category": "looks"},
    {"name": "looks_nextcostume", "label": "Next Costume", "category": "looks"}, {"name": "looks_switchbackdropto", "label": "Switch Backdrop To", "category": "looks"},
    {"name": "looks_backdrops", "label": "Backdrops", "category": "looks"}, {"name": "looks_nextbackdrop", "label": "Next Backdrop", "category": "looks"},
    {"name": "looks_changesizeby", "label": "Change Size By", "category": "looks"}, {"name": "looks_setsizeto", "label": "Set Size To", "category": "looks"},
    {"name": "looks_changeeffectby", "label": "Change Effect By", "category": "looks"}, {"name": "looks_seteffectto", "label": "Set Effect To", "category": "looks"},
    {"name": "looks_cleargraphiceffects", "label": "Clear Graphic Effects", "category": "looks"}, {"name": "looks_show", "label": "Show", "category": "looks"},
    {"name": "looks_hide", "label": "Hide", "category": "looks"}, {"name": "looks_gotofrontback", "label": "Go to Front/Back Layer", "category": "looks"},
    {"name": "looks_goforwardbackwardlayers", "label": "Go Forward/Backwards Layers", "category": "looks"}, {"name": "looks_costumenumbername", "label": "Costume Number Name", "category": "looks"},
    {"name": "looks_backdropnumbername", "label": "Backdrop Number Name", "category": "looks"}, {"name": "looks_size", "label": "Size", "category": "looks"},
    {"name": "looks_thinkforsecs", "label": "Think for Secs", "category": "looks"}, {"name": "looks_think", "label": "Think", "category": "looks"},
    {"name": "operator_add", "label": "Add", "category": "operators"}, {"name": "operator_subtract", "label": "Subtract", "category": "operators"},
    {"name": "operator_random", "label": "Random", "category": "operators"}, {"name": "operator_gt", "label": "Greater Than", "category": "operators"},
    {"name": "operator_lt", "label": "Less Than", "category": "operators"}, {"name": "operator_equals", "label": "Equals", "category": "operators"},
    {"name": "operator_and", "label": "And", "category": "operators"}, {"name": "operator_round", "label": "Round", "category": "operators"},
    {"name": "operator_mathop", "label": "Other Math Operation", "category": "operators"}, {"name": "operator_or", "label": "Or", "category": "operators"},
    {"name": "operator_not", "label": "Not", "category": "operators"}, {"name": "operator_join", "label": "Join", "category": "operators"},
    {"name": "operator_letter_of", "label": "Letter of", "category": "operators"}, {"name": "operator_length", "label": "Length of", "category": "operators"},
    {"name": "operator_contains", "label": "Parameter Contains", "category": "operators"}, {"name": "operator_mod", "label": "Modulo", "category": "operators"},
    {"name": "operator_multiply", "label": "Multiply", "category": "operators"}, {"name": "operator_divide", "label": "Divide", "category": "operators"},
    {"name": "sensing_touchingobject", "label": "Touching Object", "category": "sensing"}, {"name": "sensing_touchingobjectmenu", "label": "Touching Specific Object", "category": "sensing"},
    {"name": "sensing_touchingcolor", "label": "Touch Color", "category": "sensing"}, {"name": "sensing_coloristouchingcolor", "label": "Color is Touching Color", "category": "sensing"},
    {"name": "sensing_distanceto", "label": "Distance To Object", "category": "sensing"}, {"name": "sensing_distancetomenu", "label": "Distance to Specific Object", "category": "sensing"},
    {"name": "sensing_keypressed", "label": "Key Pressed", "category": "sensing"}, {"name": "sensing_keyoptions", "label": "Key Options", "category": "sensing"},
    {"name": "sensing_mousedown", "label": "Mouse Down", "category": "sensing"}, {"name": "sensing_mousex", "label": "Mouse X", "category": "sensing"},
    {"name": "sensing_mousey", "label": "Mouse Y", "category": "sensing"}, {"name": "sensing_setdragmode", "label": "Set Drag Mode", "category": "sensing"},
    {"name": "sensing_loudness", "label": "Loudness", "category": "sensing"}, {"name": "sensing_timer", "label": "Timer", "category": "sensing"},
    {"name": "sensing_resettimer", "label": "Reset Timer", "category": "sensing"}, {"name": "sensing_of", "label": "Sensing Of", "category": "sensing"},
    {"name": "sensing_of_object_menu", "label": "Sensing of Object", "category": "sensing"}, {"name": "sensing_current", "label": "Current Time Variable", "category": "sensing"},
    {"name": "sensing_dayssince2000", "label": "Days Since 2000", "category": "sensing"}, {"name": "sensing_username", "label": "Username", "category": "sensing"},
    {"name": "sensing_askandwait", "label": "Ask and Wait", "category": "sensing"}, {"name": "sensing_answer", "label": "Answer", "category": "sensing"},
    {"name": "sound_sounds_menu", "label": "Sounds Menu", "category": "sound"}, {"name": "sound_playuntildone", "label": "Play Until Done", "category": "sound"},
    {"name": "sound_stopallsounds", "label": "Stop All Sounds", "category": "sound"}, {"name": "sound_changeeffectby", "label": "Change Effect By", "category": "sound"},
    {"name": "sound_seteffectto", "label": "Set Effect To", "category": "sound"}, {"name": "sound_cleareffects", "label": "Clear Effects", "category": "sound"},
    {"name": "sound_changevolumeby", "label": "Change Volume By", "category": "sound"}, {"name": "sound_setvolumeto", "label": "Set Volume To", "category": "sound"},
    {"name": "sound_volume", "label": "Volume", "category": "sound"}, {"name": "sound_play", "label": "Play", "category": "sound"},
    {"name": "data_showvariable", "label": "Show Variable", "category": "variables"}, {"name": "data_hidevariable", "label": "Hide Variable", "category": "variables"},
    {"name": "procedures_definition", "label": "Block Definition", "category": "more_blocks"}, {"name": "procedures_prototype", "label": "Block Prototype", "category": "more_blocks"},
    {"name": "procedures_call", "label": "Block Call", "category": "more_blocks"},
    {"name": "data_setvariableto", "label": "Set Variable To", "category": "variables"}, {"name": "data_changevariableby", "label": "Change Variable By", "category": "variables"}]

motion_blocks = ["motion_movesteps", "motion_turnright", "motion_turnleft", "motion_goto",
    "motion_goto_menu", "motion_gotoxy", "motion_glideto", "motion_glideto_menu",
    "motion_glidesecstoxy", "motion_pointindirection", "motion_pointtowards_menu", "motion_pointtowards", "motion_changexby",
    "motion_setx", "motion_changeyby", "motion_sety", "motion_ifonedgebounce",
    "motion_setrotationstyle", "motion_xposition", "motion_yposition", "motion_direction"]

control_blocks = ["control_wait", "control_repeat", "control_forever", "control_if", "control_if_else",
    "control_wait_until", "control_repeat_until", "control_stop", "control_start_as_clone",
    "control_create_clone_of", "control_create_clone_of_menu", "control_delete_this_clone"]

event_blocks = ["event_whenflagclicked", "event_whenkeypressed", "event_whenthisspriteclicked", "event_whenflagclicked",
    "event_whenbackdropswitchesto", "event_whengreaterthan", "event_whenbroadcastreceived",
    "event_broadcast", "event_broadcastandwait"]

looks_blocks = ["looks_sayforsecs", "looks_say", "looks_thinkforsecs", "looks_think", "looks_switchcostumeto", "looks_costume", "looks_nextcostume",
    "looks_switchbackdropto", "looks_backdrops", "looks_nextbackdrop", "looks_changesizeby", "looks_setsizeto",
    "looks_changeeffectby", "looks_seteffectto", "looks_cleargraphiceffects", "looks_show", "looks_hide",
    "looks_gotofrontback", "looks_goforwardbackwardlayers", "looks_costumenumbername",  "looks_backdropnumbername", "looks_size"]

operator_blocks = ["operator_add", "operator_subtract", "operator_multiply", "operator_divide", "operator_random",
    "operator_gt", "operator_lt", "operator_equals", "operator_and", "operator_or", "operator_not", "operator_join",
    "operator_letter_of", "operator_length", "operator_contains", "operator_mod", "operator_round", "operator_mathop"]

sensing_blocks = ["sensing_touchingobject", "sensing_touchingobjectmenu", "sensing_touchingcolor", "sensing_coloristouchingcolor",
    "sensing_distanceto", "sensing_distancetomenu", "sensing_askandwait", "sensing_answer", "sensing_keypressed", "sensing_keyoptions",
    "sensing_mousedown", "sensing_mousex", "sensing_mousey", "sensing_setdragmode", "sensing_loudness", "sensing_timer",
    "sensing_resettimer", "sensing_of", "sensing_of_object_menu", "sensing_current", "sensing_dayssince2000", "sensing_username"]

sound_blocks = ["sound_sounds_menu", "sound_playuntildone", "sound_play", "sound_stopallsounds", "sound_changeeffectby", "sound_seteffectto",
    "sound_cleareffects", "sound_changevolumeby", "sound_setvolumeto", "sound_volume"]

variable_blocks = ["data_setvariableto", "data_changevariableby", "data_showvariable", "data_hidevariable"]

my_blocks_blocks = ["procedures_definition", "procedures_prototype", "procedures_call"]