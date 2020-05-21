# See https://github.com/GSE-CCL/getting-unstuck-web/blob/schema_edit/lib/schema.py#L54 for documentation of the schema

validated = {
    # For these, there's a minimum # in the schema. T/F whether satisfied.
    "min_instructions_length": True,
    "min_description_length": True,
    "min_comments_made": True,
    "min_blockify": {
        "comments": True,
        "costumes": False,
        "sounds": True,
        "sprites": True,
        "variables": False
    },

    # Required text is a list of lists. Each outer list has to be satisfied to meet the schema requirements.
    # The validator tells you the index of the text option used from the inner options.
    "required_text": [
        0, # The user used the 0th choice for the 0th requirement
        1, # The user used the 1st choice for the 1st requirement
        -1 # The user didn't meet the 2nd requirement
    ],

    # Each category here is mapped to the min number that must be in the project. Not every category may be listed in a schema, so you should handle for that.
    # True/False depending on if min # of blocks of each category in the project
    "required_block_categories": {
        "motion": True,
        "control": False
    },

    # One requirement of each element must be met. This list tells us which key of the options is met by the project. If none, it's False.
    "required_blocks": [
        "motion_movesteps",
        False
    ]
}