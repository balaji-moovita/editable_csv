from qgis.core import QgsProject, QgsVectorLayer, QgsVectorFileWriter, Qgis
from qgis.gui import QgsMessageBar
from PyQt5.QtWidgets import QAction, QToolBar, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
import os.path
import csv

class EditableCSV:
    def __init__(self, iface):
        self.iface = iface
        self.toolbar = None
        self.actions = []

    def initGui(self):
        self.toolbar = QToolBar("Editable CSV")
        self.iface.addToolBar(self.toolbar)

        # Create the actions
        self.import_csv_action = QAction(QIcon(os.path.dirname(__file__) + "/icon.png"), "Import CSV", self.iface.mainWindow())
        self.delete_point_action = QAction(QIcon(os.path.dirname(__file__) + "/delete.png"), "Delete Selected Point(s)", self.iface.mainWindow())
        self.edit_attributes_action = QAction(QIcon(os.path.dirname(__file__) + "/edit_attributes.png"), "Edit Attributes", self.iface.mainWindow())
        self.undo_action = QAction(QIcon(os.path.dirname(__file__) + "/undo.png"), "Undo Last Action", self.iface.mainWindow())
        self.save_to_csv_action = QAction(QIcon(os.path.dirname(__file__) + "/save.png"), "Save to CSV", self.iface.mainWindow())
        self.save_multiple_action = QAction(QIcon(os.path.dirname(__file__) + "/save_multiple.png"), "Save Multiple CSVs", self.iface.mainWindow())

        # Connect to signals
        self.import_csv_action.triggered.connect(self.import_csv)
        self.delete_point_action.triggered.connect(self.delete_point)
        self.edit_attributes_action.triggered.connect(self.edit_attributes)
        self.undo_action.triggered.connect(self._undo_action)
        self.save_to_csv_action.triggered.connect(self.save_to_csv)
        self.save_multiple_action.triggered.connect(self.save_multiple_csvs)

        # Add actions to the toolbar
        self.toolbar.addAction(self.import_csv_action)
        self.toolbar.addAction(self.delete_point_action)
        self.toolbar.addAction(self.edit_attributes_action)
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.save_to_csv_action)
        self.toolbar.addAction(self.save_multiple_action)

        # Add actions to the list for unloading
        self.actions = [self.import_csv_action, self.delete_point_action, self.edit_attributes_action, self.undo_action, self.save_to_csv_action, self.save_multiple_action]

    def unload(self):
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
        if self.toolbar:
            del self.toolbar

    def import_csv(self):
        from .import_csv_dialog import ImportCsvDialog
        
        file_names, _ = QFileDialog.getOpenFileNames(self.iface.mainWindow(), "Select CSV Files", "", "CSV Files (*.csv)")
        
        if not file_names:
            return # User cancelled

        for file_path in file_names:
            dialog = ImportCsvDialog(self.iface.mainWindow())
            dialog.file_edit.setText(file_path) # Pre-fill the file path
            
            if dialog.exec_():
                options = dialog.get_options()
                delimiter = options["delimiter"]
                x_field = options["x_field"]
                y_field = options["y_field"]

                uri = f"file://{file_path}?delimiter={delimiter}&xField={x_field}&yField={y_field}"
                source_layer = QgsVectorLayer(uri, "source_csv_temp", "delimitedtext")

                if not source_layer.isValid():
                    self.iface.messageBar().pushMessage("Error", f"Failed to read CSV file: {os.path.basename(file_path)}", level=Qgis.Critical)
                    continue

                layer_name = os.path.basename(file_path).replace('.csv', '')
                crs = source_layer.crs().authid() if source_layer.crs().isValid() else "EPSG:4326"
                mem_layer = QgsVectorLayer(f"Point?crs={crs}", layer_name, "memory")

                mem_provider = mem_layer.dataProvider()
                mem_provider.addAttributes(source_layer.fields())
                mem_layer.updateFields()

                mem_layer.startEditing()
                for feature in source_layer.getFeatures():
                    mem_provider.addFeature(feature)
                mem_layer.commitChanges()

                mem_layer.setCustomProperty('original_delimiter', delimiter)
                mem_layer.setCustomProperty('original_x_field', x_field)
                mem_layer.setCustomProperty('original_y_field', y_field)
                mem_layer.setCustomProperty('original_file_path', file_path)

                QgsProject.instance().addMapLayer(mem_layer)
                self.iface.messageBar().pushMessage("Success", f"Layer '{layer_name}' added successfully as an editable layer.", level=Qgis.Success)
            else:
                self.iface.messageBar().pushMessage("Info", f"Import of {os.path.basename(file_path)} cancelled.", level=Qgis.Info)

    

    def delete_point(self):
        layer = self.iface.activeLayer()
        if not layer:
            self.iface.messageBar().pushMessage("Warning", "Please select a layer.", level=Qgis.Warning)
            return

        if not layer.isEditable():
            self.iface.messageBar().pushMessage("Warning", "Please toggle editing on the selected layer first.", level=Qgis.Warning)
            return

        selected_features = layer.selectedFeatures()
        if not selected_features:
            self.iface.messageBar().pushMessage("Info", "No features selected to delete.", level=Qgis.Info)
            return

        reply = QMessageBox.question(self.iface.mainWindow(), 'Delete Features', 
                                     f"Are you sure you want to delete {len(selected_features)} selected feature(s)?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            layer.deleteFeatures([f.id() for f in selected_features])
            self.iface.messageBar().pushMessage("Success", f"{len(selected_features)} feature(s) deleted.", level=Qgis.Success)
        else:
            self.iface.messageBar().pushMessage("Info", "Deletion cancelled.", level=Qgis.Info)

    def _undo_action(self):
        self.iface.undoStack().undo()

    def save_to_csv(self):
        import csv
        layer = self.iface.activeLayer()
        if not layer:
            self.iface.messageBar().pushMessage("Warning", "Please select a layer to save.", level=Qgis.Warning)
            return

        original_delimiter = layer.customProperty('original_delimiter')
        original_x_field = layer.customProperty('original_x_field')
        original_y_field = layer.customProperty('original_y_field')

        if not all([original_delimiter, original_x_field, original_y_field]):
            self.iface.messageBar().pushMessage("Error", "Cannot save: Original CSV properties not found for this layer.", level=Qgis.Critical)
            return

        file_name, _ = QFileDialog.getSaveFileName(self.iface.mainWindow(), "Save CSV File", "", "CSV Files (*.csv)")
        if file_name:
            try:
                with open(file_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=original_delimiter)

                    fields = [field.name() for field in layer.fields()]
                    writer.writerow(fields)

                    for feature in layer.getFeatures():
                        row = []
                        for field_name in fields:
                            if field_name == original_x_field:
                                row.append(feature.geometry().asPoint().x())
                            elif field_name == original_y_field:
                                row.append(feature.geometry().asPoint().y())
                            else:
                                row.append(feature[field_name])
                        writer.writerow(row)

                self.iface.messageBar().pushMessage("Success", f"Layer saved to {file_name}", level=Qgis.Success)
            except Exception as e:
                self.iface.messageBar().pushMessage("Error", f"Error saving CSV: {e}", level=Qgis.Critical)

    def edit_attributes(self):
        layer = self.iface.activeLayer()
        if not layer:
            self.iface.messageBar().pushMessage("Warning", "Please select a layer.", level=Qgis.Warning)
            return

        selected_features = layer.selectedFeatures()

        if len(selected_features) == 1:
            feature = selected_features[0]
            self.iface.openFeatureForm(layer, feature)
        else:
            # If 0 or more than 1 feature is selected, open the attribute table
            self.iface.showAttributeTable(layer)

    def save_multiple_csvs(self):
        from .save_multiple_csv_dialog import SaveMultipleCsvDialog
        
        plugin_layers = []
        for layer_id in QgsProject.instance().mapLayers():
            layer = QgsProject.instance().mapLayers()[layer_id]
            if layer.customProperty('original_delimiter') and layer.customProperty('original_x_field'):
                plugin_layers.append(layer)
        
        if not plugin_layers:
            self.iface.messageBar().pushMessage("Info", "No editable CSV layers found in the project.", level=Qgis.Info)
            return

        dialog = SaveMultipleCsvDialog(self.iface.mainWindow())
        if dialog.exec_():
            folder_path = dialog.get_selected_folder()
            if folder_path:
                for layer in plugin_layers:
                    # Get original filename from custom property
                    original_file_path = layer.customProperty('original_file_path')
                    if original_file_path:
                        file_name = os.path.basename(original_file_path)
                        new_file_path = os.path.join(folder_path, file_name)
                        self._save_single_layer_to_csv(layer, new_file_path)
                    else:
                        # Fallback to layer name if original path not found
                        file_name = f"{layer.name()}.csv"
                        new_file_path = os.path.join(folder_path, file_name)
                        self._save_single_layer_to_csv(layer, new_file_path)

    def _save_single_layer_to_csv(self, layer, file_path):
        import csv
        original_delimiter = layer.customProperty('original_delimiter')
        original_x_field = layer.customProperty('original_x_field')
        original_y_field = layer.customProperty('original_y_field')

        if not all([original_delimiter, original_x_field, original_y_field]):
            self.iface.messageBar().pushMessage("Error", f"Cannot save layer {layer.name()}: Original CSV properties not found.", level=Qgis.Critical)
            return

        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=original_delimiter)

                fields = [field.name() for field in layer.fields()]
                writer.writerow(fields)

                for feature in layer.getFeatures():
                    row = []
                    for field_name in fields:
                        if field_name == original_x_field:
                            row.append(feature.geometry().asPoint().x())
                        elif field_name == original_y_field:
                            row.append(feature.geometry().asPoint().y())
                        else:
                            row.append(feature[field_name])
                    writer.writerow(row)

            self.iface.messageBar().pushMessage("Success", f"Layer '{layer.name()}' saved to {file_path}", level=Qgis.Success)
        except Exception as e:
            self.iface.messageBar().pushMessage("Error", f"Error saving layer {layer.name()} to CSV: {e}", level=Qgis.Critical)
