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
*   **Edit Attributes:** Opens an attribute form for a single selected point, or the attribute table for multiple selected points.
*   **Undo Last Action:** Undoes the last action (e.g., point deletion).
*   **Save to CSV:** Saves the active layer to a new CSV file.
*   **Save Multiple CSVs:** Saves all modified CSV layers to a selected folder.

### Moving Points

To move points, you need to use the built-in QGIS tools:
1.  Select the layer you want to edit in the Layers panel.
2.  Toggle editing by clicking the pencil icon in the toolbar or by right-clicking the layer and selecting `Toggle Editing`.
3.  Use the `Vertex Tool` from the `Digitizing Toolbar` to move the points. Select a point and drag it to a new location.
4.  When you are done, toggle editing off and save the changes.

### Editing Points

#### Adding Points
To add new points, you need to use the built-in QGIS "Add Point Feature" tool:
1.  Select the layer you want to edit in the Layers panel.
2.  Toggle editing on for the layer.
3.  Click on the "Add Point Feature" button in the `Digitizing Toolbar`.
4.  Click on the map to add a new point. You will be prompted to enter the attribute values for the new point.

#### Editing Attributes
To edit the attributes of existing points:
1.  Select the point(s) you want to edit.
2.  Click the **Edit Attributes** button in the plugin's toolbar.
    *   If you have a single point selected, a form will open to edit its attributes.
    *   If you have multiple points selected, the attribute table will open.
3.  You can also open the attribute table by right-clicking the layer and selecting `Open Attribute Table`.
