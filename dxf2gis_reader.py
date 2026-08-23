"""
dxf2gis_reader.py

This module is responsible only for opening a DXF file through GDAL
and OGR, and reporting what is inside it. It does not write any
output files. It uses GDAL and OGR through QGIS, as described in the
project proposal, rather than writing a custom DXF parser.

GDAL's DXF driver exposes all entities in a DXF file through a single
layer called entities. Each feature in that layer carries a field
called Layer, which holds the original CAD layer name the entity
belonged to in the drawing.

By default, GDAL treats closed polylines as lines, even though in
CAD drawings a closed polyline usually represents a filled shape such
as a building footprint or a sports court. We turn on the GDAL setting
DXF_CLOSED_LINE_AS_POLYGON so that closed polylines are correctly
reported as polygons instead of lines.
"""

from osgeo import gdal
from qgis.core import QgsVectorLayer
from .dxf2gis_classifier import classify_geometry_type


def open_dxf_layer(dxf_path):
    """
    Opens a DXF file using GDAL and OGR and returns it as a QGIS
    vector layer containing all entities from the drawing.

    Raises a ValueError if the file cannot be opened.
    """

    # Tell GDAL to treat closed polylines as polygons rather than
    # lines. This must be set before the layer is opened.
    gdal.SetConfigOption("DXF_CLOSED_LINE_AS_POLYGON", "YES")

    # The entities layer is the standard name GDAL uses to expose
    # all drawing entities inside a DXF file.
    uri = dxf_path + "|layername=entities"
    layer = QgsVectorLayer(uri, "dxf_entities", "ogr")

    if not layer.isValid():
        raise ValueError("Could not open DXF file: " + str(dxf_path))

    return layer


def read_dxf_summary(dxf_path):
    """
    Opens a DXF file and counts how many features exist for each
    combination of CAD layer name and geometry type.

    Returns a dictionary where each key is a tuple of
    (cad_layer_name, geometry_type_name) and each value is the
    number of features found with that combination.
    """

    layer = open_dxf_layer(dxf_path)

    field_names = [field.name() for field in layer.fields()]
    has_layer_field = "Layer" in field_names

    counts = {}

    for feature in layer.getFeatures():
        if has_layer_field:
            cad_layer = feature["Layer"]
        else:
            cad_layer = "unknown"

        geometry_type_name = classify_geometry_type(feature.geometry())
        if geometry_type_name is None:
            geometry_type_name = "no geometry"

        key = (cad_layer, geometry_type_name)
        counts[key] = counts.get(key, 0) + 1

    return counts