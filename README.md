# DXF2GIS

A QGIS plugin that converts DXF CAD drawings into clean GIS data. It splits a drawing into separate point, line and polygon layers, lets the user assign a coordinate reference system, and exports the result to GeoPackage, Shapefile or GeoJSON.

DXF files carry no coordinate reference system and usually mix points, lines and polygons together on the same CAD layer, which makes bringing survey and engineering drawings into a GIS a slow, manual process. DXF2GIS automates that conversion. It runs entirely on libraries bundled with QGIS, so it needs no extra installation and works the same on Windows, Linux and macOS.

## Team

Mary Muthee, Mberede Benedict, Meenu Anil

## Features

- Reads a DXF file and splits its contents into point, line and polygon layers
- Lets the user assign a coordinate reference system, since DXF files carry none
- Exports to GeoPackage, Shapefile or GeoJSON
- Optionally exports each original CAD layer as its own file, with file and layer names cleaned up automatically
- Preserves the attributes GDAL exposes, including CAD layer name, entity handle, line type and text
- Runs inside the QGIS Processing framework, so it supports batch runs and can be used from the Python console or in a Processing model

## Installation

### From a ZIP file

1. In QGIS, go to Plugins, then Manage and Install Plugins.
2. Click Install from ZIP.
3. Select the dxf2gis.zip file.
4. Click Install Plugin.

### From source, for development

1. Clone this repository into your QGIS plugins folder.
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
2. Restart QGIS, or use the Plugin Reloader plugin during development.
3. In QGIS, go to Plugins, then Manage and Install Plugins, then Installed, and tick the checkbox next to DXF2GIS.

## Usage

1. In QGIS, open Processing, then Toolbox.
2. Find Convert DXF to GIS layers under the DXF2GIS group.
3. Choose your input DXF file.
4. Choose the coordinate reference system your survey or drawing was produced in. DXF files do not carry this information, so you must set it yourself.
5. Choose where to save the point, line and polygon outputs, or leave them on the temporary defaults to inspect the result first.
6. Optionally, tick Also export each CAD layer separately and choose a folder, to also get one file per original CAD layer.
7. Click Run.

## Known limitations

- DWG files are not supported. DWG is a proprietary format with no free reader available through GDAL or OGR, which this plugin relies on for all parsing. Export to DXF from your CAD software first.
- Conversion time and memory use scale with the number of entities in the drawing. A typical single site survey converts in well under a second. Very large datasets, such as an entire city in one file, take noticeably longer and use more memory, but have been tested successfully.

## Bug reports and feature requests

Please use the [Issues tab](https://github.com/marymuthee/dxf2gis/issues) on this repository.


