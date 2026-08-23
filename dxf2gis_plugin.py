"""
dxf2gis_plugin.py

Entry point class for the DXF2GIS plugin.
QGIS calls initGui() when the plugin is enabled, and unload() when it is
disabled or QGIS closes. This class does not do the actual DXF conversion.
Its only job is to register our Processing algorithm with QGIS so it
shows up in the Processing Toolbox.
"""

from qgis.core import QgsApplication
from .dxf2gis_provider import Dxf2GisProvider


class Dxf2GisPlugin:
    def __init__(self, iface):
        # iface gives access to the QGIS application interface
        # such as the map canvas and menus. We do not need it yet,
        # but QGIS always passes it in, so we store it for later use.
        self.iface = iface
        self.provider = None

    def initGui(self):
        # Runs once when the plugin is loaded and enabled.
        # Create our Processing provider and register it with QGIS
        # so our algorithm appears in the Processing Toolbox.
        self.provider = Dxf2GisProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        # Runs when the plugin is disabled or unloaded.
        # Remove our provider from the registry so QGIS does not
        # keep a leftover reference around.
        QgsApplication.processingRegistry().removeProvider(self.provider)