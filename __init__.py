def classFactory(iface):
    from .dxf2gis_plugin import Dxf2GisPlugin
    return Dxf2GisPlugin(iface)