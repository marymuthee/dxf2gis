"""
dxf2gis_algorithm.py

This file defines the actual Processing algorithm for DXF2GIS.
It takes an input DXF file and a target coordinate reference system,
then produces three output layers, points, lines and polygons, using
the reader module to open the file and the classifier module to sort
features by geometry type.

It also offers an optional feature, split by CAD layer. When turned
on, in addition to the three merged output layers, the algorithm
writes one extra GeoPackage file per original CAD layer and geometry
type combination, into a folder the user chooses. File and layer
names are cleaned up using the sanitize_name helper, since CAD layer
names often contain spaces. A second checkbox controls whether these
extra files are also loaded into the current QGIS project.
"""

import os
import os
from qgis.PyQt.QtGui import QIcon

from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingParameterFile,
    QgsProcessingParameterCrs,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterFeatureSink,
    QgsFeatureSink,
    QgsWkbTypes,
    QgsVectorLayer,
    QgsVectorFileWriter,
)
from .dxf2gis_reader import open_dxf_layer
from .dxf2gis_classifier import split_features_by_geometry
from .dxf2gis_utils import sanitize_name


GEOMETRY_TYPE_TO_WKT_WORD = {
    "point": "Point",
    "line": "LineString",
    "polygon": "Polygon",
}


class Dxf2GisAlgorithm(QgsProcessingAlgorithm):

    INPUT_DXF = "INPUT_DXF"
    TARGET_CRS = "TARGET_CRS"
    OUTPUT_POINTS = "OUTPUT_POINTS"
    OUTPUT_LINES = "OUTPUT_LINES"
    OUTPUT_POLYGONS = "OUTPUT_POLYGONS"
    SPLIT_BY_LAYER = "SPLIT_BY_LAYER"
    SPLIT_OUTPUT_FOLDER = "SPLIT_OUTPUT_FOLDER"
    LOAD_SPLIT_LAYERS = "LOAD_SPLIT_LAYERS"

    def name(self):
        return "dxf2gis_convert"

    def displayName(self):
        return "Convert DXF to GIS layers"

    def group(self):
        return "DXF2GIS"

    def groupId(self):
        return "dxf2gis"

    def shortHelpString(self):
        return (
            "Converts a DXF drawing into separate point, line and "
            "polygon GIS layers. A DXF file does not carry a "
            "coordinate reference system, so you must choose one "
            "for the output layers. Optionally, each original CAD "
            "layer can also be exported as its own file, and those "
            "files can be loaded into the project automatically."
        )

    def createInstance(self):
        return Dxf2GisAlgorithm()
    
    def icon(self):
        plugin_folder = os.path.dirname(__file__)
        icon_path = os.path.join(plugin_folder, "icon.png")
        return QIcon(icon_path)

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_DXF,
                "Input DXF file",
                extension="dxf",
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.TARGET_CRS,
                "Target coordinate reference system",
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_POINTS,
                "Output point layer",
                type=QgsProcessing.TypeVectorPoint,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LINES,
                "Output line layer",
                type=QgsProcessing.TypeVectorLine,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_POLYGONS,
                "Output polygon layer",
                type=QgsProcessing.TypeVectorPolygon,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SPLIT_BY_LAYER,
                "Also export each CAD layer separately",
                defaultValue=False,
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.SPLIT_OUTPUT_FOLDER,
                "Folder for per CAD layer exports (used only if the option above is checked)",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_SPLIT_LAYERS,
                "Load per CAD layer exports into the project",
                defaultValue=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_dxf = self.parameterAsFile(parameters, self.INPUT_DXF, context)
        target_crs = self.parameterAsCrs(parameters, self.TARGET_CRS, context)
        split_by_layer = self.parameterAsBoolean(parameters, self.SPLIT_BY_LAYER, context)
        split_output_folder = self.parameterAsString(parameters, self.SPLIT_OUTPUT_FOLDER, context)
        load_split_layers = self.parameterAsBoolean(parameters, self.LOAD_SPLIT_LAYERS, context)

        feedback.pushInfo("Reading DXF file: " + str(input_dxf))
        source_layer = open_dxf_layer(input_dxf)
        fields = source_layer.fields()

        field_names = [field.name() for field in fields]
        has_layer_field = "Layer" in field_names

        sink_points, dest_id_points = self.parameterAsSink(
            parameters, self.OUTPUT_POINTS, context,
            fields, QgsWkbTypes.Point, target_crs,
        )
        sink_lines, dest_id_lines = self.parameterAsSink(
            parameters, self.OUTPUT_LINES, context,
            fields, QgsWkbTypes.LineString, target_crs,
        )
        sink_polygons, dest_id_polygons = self.parameterAsSink(
            parameters, self.OUTPUT_POLYGONS, context,
            fields, QgsWkbTypes.Polygon, target_crs,
        )

        point_count = 0
        line_count = 0
        polygon_count = 0

        # This dictionary collects features for the optional split by
        # CAD layer export. Each key is a tuple of
        # (cad_layer_name, geometry_type_name), and each value is a
        # list of features belonging to that combination.
        grouped_for_split = {}

        for geometry_type_name, feature in split_features_by_geometry(source_layer):
            if geometry_type_name == "point":
                sink_points.addFeature(feature, QgsFeatureSink.FastInsert)
                point_count += 1
            elif geometry_type_name == "line":
                sink_lines.addFeature(feature, QgsFeatureSink.FastInsert)
                line_count += 1
            elif geometry_type_name == "polygon":
                sink_polygons.addFeature(feature, QgsFeatureSink.FastInsert)
                polygon_count += 1
            else:
                continue

            if split_by_layer:
                if has_layer_field:
                    cad_layer = feature["Layer"]
                else:
                    cad_layer = "unknown"
                key = (cad_layer, geometry_type_name)
                grouped_for_split.setdefault(key, []).append(feature)

            if feedback.isCanceled():
                break

        feedback.pushInfo("Points written: " + str(point_count))
        feedback.pushInfo("Lines written: " + str(line_count))
        feedback.pushInfo("Polygons written: " + str(polygon_count))

        if split_by_layer:
            if not split_output_folder:
                feedback.pushInfo(
                    "Split by CAD layer was requested, but no output "
                    "folder was chosen, so this step was skipped."
                )
            else:
                feedback.pushInfo("Writing per CAD layer files to: " + str(split_output_folder))
                self.write_split_layers(
                    grouped_for_split, fields, target_crs,
                    split_output_folder, context, feedback,
                    load_split_layers,
                )

        return {
            self.OUTPUT_POINTS: dest_id_points,
            self.OUTPUT_LINES: dest_id_lines,
            self.OUTPUT_POLYGONS: dest_id_polygons,
        }

    def write_split_layers(self, grouped_for_split, fields, target_crs,
                            output_folder, context, feedback,
                            load_split_layers):
        # Writes one small GeoPackage file per CAD layer and geometry
        # type combination, using cleaned up, file system safe names.
        # If load_split_layers is True, each file is also registered
        # with the processing context so QGIS opens it automatically
        # once the algorithm finishes.
        for (cad_layer, geometry_type_name), features in grouped_for_split.items():
            safe_layer_name = sanitize_name(cad_layer)
            wkt_word = GEOMETRY_TYPE_TO_WKT_WORD.get(geometry_type_name, "Unknown")

            file_name = safe_layer_name + "_" + geometry_type_name + ".gpkg"
            output_path = os.path.join(output_folder, file_name)

            uri = wkt_word + "?crs=" + target_crs.authid()
            temp_layer = QgsVectorLayer(uri, safe_layer_name, "memory")
            temp_provider = temp_layer.dataProvider()
            temp_provider.addAttributes(fields)
            temp_layer.updateFields()
            temp_provider.addFeatures(features)

            save_options = QgsVectorFileWriter.SaveVectorOptions()
            save_options.driverName = "GPKG"
            save_options.layerName = safe_layer_name

            QgsVectorFileWriter.writeAsVectorFormatV3(
                temp_layer,
                output_path,
                context.transformContext(),
                save_options,
            )

            feedback.pushInfo(
                "  Wrote " + str(len(features)) + " " + geometry_type_name +
                " feature(s) for CAD layer '" + str(cad_layer) +
                "' to " + output_path
            )

            if load_split_layers:
                display_name = safe_layer_name + " (" + geometry_type_name + ")"
                layer_uri = output_path + "|layername=" + safe_layer_name
                layer_details = QgsProcessingContext.LayerDetails(
                    display_name, context.project(), display_name
                )
                context.addLayerToLoadOnCompletion(layer_uri, layer_details)