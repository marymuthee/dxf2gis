"""
dxf2gis_utils.py

Small helper functions shared across the plugin. Currently this
holds one function, sanitize_name, which cleans up CAD layer names
so they are safe to use as file names and GeoPackage layer names.

CAD layer names often contain spaces or punctuation, for example
Road edge or Tennis Court, which are fine inside a drawing but can
cause problems in file names on some systems. This function replaces
anything that is not a letter, a number or an underscore with an
underscore, and cleans up the result.
"""

import re


def sanitize_name(name):
    """
    Takes any text, for example a CAD layer name, and returns a
    version safe to use as a file name or a GeoPackage layer name.
    """

    if name is None:
        name = "layer"

    text = str(name).strip()

    # Replace any character that is not a letter, digit or
    # underscore with an underscore.
    text = re.sub(r"[^A-Za-z0-9_]+", "_", text)

    # Collapse multiple underscores in a row into a single one.
    text = re.sub(r"_+", "_", text)

    # Remove leading or trailing underscores left over from the
    # replacements above.
    text = text.strip("_")

    if not text:
        text = "layer"

    return text