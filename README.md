# Editable CSV Geo QGIS Plugin

This plugin allows you to import CSV files as editable in-memory point layers in QGIS. You can then add, delete, and edit points and their attributes, and save the changes back to CSV files.

## Installation

1.  Open QGIS.
2.  Go to `Plugins` -> `Manage and Install Plugins...`.
3.  Go to the `Install from ZIP` tab.
4.  Click on the `...` button and select the ZIP file of this plugin.
5.  Click `Install Plugin`.
6.  Make sure the plugin is enabled in the `Installed` tab.

Alternatively, you can manually install the plugin:
1.  Locate your QGIS plugins directory. You can find it by going to `Settings` -> `User Profiles` -> `Open Active Profile Folder`, and then navigating to `python/plugins`.
2.  Copy the `editable_csv_geo` folder into the plugins directory.
3.  Restart QGIS.

## Usage

### Toolbar

The plugin provides a toolbar with the following tools:

*   **Import CSV:** Imports one or more CSV files as new editable layers. You will be prompted to select the delimiter and the X and Y fields.
*   **Delete Selected Point(s):** Deletes the selected points from the active layer.
*   **Save to CSV:** Saves the active layer to a new CSV file.
*   **Save Multiple CSVs:** Saves all modified CSV layers to a selected folder.

### Editing and Moving Points

To add, move, or edit points and their attributes, you need to use the built-in QGIS tools:
1.  Select the layer you want to edit in the Layers panel.
2.  Toggle editing by clicking the pencil icon in the toolbar or by right-clicking the layer and selecting `Toggle Editing`.
3.  Use the tools from the `Digitizing Toolbar`:
    *   **Add Point Feature:** To add new points.
    *   **Vertex Tool:** To move points.
    *   **Identify Features:** To view and edit attributes of a point.
4.  When you are done, toggle editing off and save the changes.
5.  You can also edit attributes in the attribute table by right-clicking the layer and selecting `Open Attribute Table`.