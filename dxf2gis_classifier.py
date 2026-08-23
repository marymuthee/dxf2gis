"""
dxf2gis_classifier.py

This module is responsible only for deciding what geometry type each
feature belongs to, point, line or polygon. It does not read files
and it does not write files. Keeping this logic separate means we
can test it on its own and reuse it wherever we need it, following
the separation of concerns approach described in the project
proposal.
"""

from qgis.core import QgsWkbTypes


def classify_geometry_type(geometry):
    """
    Looks at a single QGIS geometry and returns a plain text label
    describing its type, one of point, line or polygon.

    Returns None if the geometry is missing, empty, or of a type we
    do not currently support.
    """

    if geometry is None or geometry.isEmpty():
        return None

    wkb_type = geometry.type()

    if wkb_type == QgsWkbTypes.PointGeometry:
        return "point"
    elif wkb_type == QgsWkbTypes.LineGeometry:
        return "line"
    elif wkb_type == QgsWkbTypes.PolygonGeometry:
        return "polygon"
    else:
        return None


def split_features_by_geometry(source_layer):
    """
    Goes through every feature in source_layer and yields pairs of
    (geometry_type_name, feature). Features with an unsupported or
    missing geometry are skipped, they are simply not yielded.

    This is a generator, meaning it produces one result at a time
    rather than building a big list in memory all at once. This
    matters for large DXF files with thousands of entities.
    """

    for feature in source_layer.getFeatures():
        geometry_type_name = classify_geometry_type(feature.geometry())
        if geometry_type_name is not None:
            yield geometry_type_name, feature