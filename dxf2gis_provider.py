"""
dxf2gis_provider.py

This file defines the Processing provider for DXF2GIS.
A provider in QGIS Processing is like a folder that groups related
algorithms together in the Processing Toolbox. Ours holds one
algorithm, the DXF conversion tool itself.
"""

import os

from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider
from .dxf2gis_algorithm import Dxf2GisAlgorithm


class Dxf2GisProvider(QgsProcessingProvider):

    def id(self):
        return "dxf2gis"

    def name(self):
        return "DXF2GIS"

    def icon(self):
        # Build the path to icon.png, which sits in the same folder
        # as this file, and use it as the icon for this provider in
        # the Processing Toolbox.
        plugin_folder = os.path.dirname(__file__)
        icon_path = os.path.join(plugin_folder, "icon.png")
        return QIcon(icon_path)

    def loadAlgorithms(self):
        self.addAlgorithm(Dxf2GisAlgorithm())