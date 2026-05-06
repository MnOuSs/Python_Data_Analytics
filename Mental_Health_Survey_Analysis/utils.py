"""
Utility functions for text cleaning and ordinal encoding.

"""

def clean_text(x):
    """
    Clean a text value by stripping whitespace, converting to lowercase,
    and removing periods. If the input is not a string, it is returned unchanged.

    """
    if isinstance(x, str):
        # Normalize text to lowercase, remove trailing/leading spaces and periods
        x = x.strip().lower().replace(".", "")
        return x
    return x

# Mapping for ordinal encoding of qualitative responses
ordinal_map = {
    "yes": 2,
    "no": 0,
    "maybe": 1,
    "not sure": 1,
    "sometimes": 1,
    "it depends": 1
}

def encode_ordinal(x):
    """
    Encode qualitative text responses into ordinal numerical values
    based on a predefined mapping. Non-string inputs are returned unchanged.

    """
    if isinstance(x, str):
        # Return mapped value; default to neutral (1) when key is missing
        return ordinal_map.get(x, 1)
    return x
