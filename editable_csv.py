from qgis.core import QgsProject, QgsVectorLayer, QgsVectorFileWriter, Qgis, QgsFeature
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
        self.import_csv_action = QAction(QIcon(os.path.dirname(__file__) + "/icon.png"), "Import Editable CSV", self.iface.mainWindow())
        self.reload_action = QAction(QIcon(os.path.dirname(__file__) + "/undo.png"), "Reload Layer from File", self.iface.mainWindow())
        self.delete_point_action = QAction(QIcon(os.path.dirname(__file__) + "/delete.png"), "Delete Selected Point(s)", self.iface.mainWindow())
        self.save_to_csv_action = QAction(QIcon(os.path.dirname(__file__) + "/save.png"), "Save selected CSV", self.iface.mainWindow())
        self.save_multiple_action = QAction(QIcon(os.path.dirname(__file__) + "/save_multiple.png"), "Save all modified CSVs", self.iface.mainWindow())

        # Connect to signals
        self.import_csv_action.triggered.connect(self.import_csv)
        self.reload_action.triggered.connect(self.reload_layer_data)
        self.delete_point_action.triggered.connect(self.delete_point)
        self.save_to_csv_action.triggered.connect(self.save_to_csv)
        self.save_multiple_action.triggered.connect(self.save_multiple_csvs)

        # Add actions to the toolbar
        self.toolbar.addAction(self.import_csv_action)
        self.toolbar.addAction(self.reload_action)
        self.toolbar.addAction(self.delete_point_action)
        self.toolbar.addAction(self.save_to_csv_action)
        self.toolbar.addAction(self.save_multiple_action)

        # Add actions to the list for unloading
        self.actions = [self.import_csv_action, self.reload_action, self.delete_point_action, self.save_to_csv_action, self.save_multiple_action]

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
            x_field = ''
            y_field = ''
            
            try:
                with open(file_path, 'r') as f:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(f.read(1024))
                    f.seek(0)
                    delimiter = dialect.delimiter
                    reader = csv.reader(f, dialect)
                    header = next(reader)
                    # Auto-select X and Y fields if present
                    for field in header:
                        if field.lower() == 'x':
                            x_field = field
                        if field.lower() == 'y':
                            y_field = field
            except Exception as e:
                print(f"Error reading CSV header: {e}")

            if len(file_names) > 1 and x_field and y_field:
                options = {
                    "file_path": file_path,
                    "delimiter": delimiter,
                    "x_field": x_field,
                    "y_field": y_field,
                    "detect_types": False,
                }
            else:
                dialog = ImportCsvDialog(self.iface.mainWindow())
                dialog.file_edit.setText(file_path) # Pre-fill the file path
                if not dialog.exec_():
                    self.iface.messageBar().pushMessage("Info", f"Import of {os.path.basename(file_path)} cancelled.", level=Qgis.Info)
                    continue
                options = dialog.get_options()

            delimiter = options["delimiter"]
            x_field = options["x_field"]
            y_field = options["y_field"]
            detect_types = "yes" if options["detect_types"] else "no"

            uri = f"file://{file_path}?delimiter={delimiter}&xField={x_field}&yField={y_field}&detectTypes={detect_types}"
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
            mem_layer.setCustomProperty('detect_types', detect_types)

            QgsProject.instance().addMapLayer(mem_layer)
            self.iface.messageBar().pushMessage("Success", f"Layer '{layer_name}' added successfully as an editable layer.", level=Qgis.Success)

    

    def reload_layer_data(self):
        layer = self.iface.activeLayer()
        if not layer:
            self.iface.messageBar().pushMessage("Warning", "Please select a layer to reload.", level=Qgis.Warning)
            return

        original_file_path = layer.customProperty('original_file_path')
        if not original_file_path:
            self.iface.messageBar().pushMessage("Warning", "This layer was not imported by the Editable CSV plugin and cannot be reloaded.", level=Qgis.Warning)
            return

        reply = QMessageBox.question(self.iface.mainWindow(), 'Reload Layer', 
                                     f"Are you sure you want to reload the layer '{layer.name()}' from its original file? Any unsaved changes will be lost.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            self.iface.messageBar().pushMessage("Info", "Reload cancelled.", level=Qgis.Info)
            return

        original_delimiter = layer.customProperty('original_delimiter')
        original_x_field = layer.customProperty('original_x_field')
        original_y_field = layer.customProperty('original_y_field')
        detect_types_str = layer.customProperty('detect_types', 'yes')

        uri = f"file://{original_file_path}?delimiter={original_delimiter}&xField={original_x_field}&yField={original_y_field}&detectTypes={detect_types_str}"
        source_layer = QgsVectorLayer(uri, "source_csv_temp_reload", "delimitedtext")

        if not source_layer.isValid():
            self.iface.messageBar().pushMessage("Error", f"Failed to read original CSV file: {os.path.basename(original_file_path)}", level=Qgis.Critical)
            return

        if source_layer.fields().count() != layer.fields().count() or \
           [f.name() for f in source_layer.fields()] != [f.name() for f in layer.fields()]:
            self.iface.messageBar().pushMessage("Warning", "The schema of the source CSV file has changed. Reloading is not supported in this case.", level=Qgis.Warning)
            return

        layer.startEditing()
        layer.deleteFeatures([f.id() for f in layer.getFeatures()])
        
        new_features = []
        for f in source_layer.getFeatures():
            new_feat = QgsFeature()
            new_feat.setGeometry(f.geometry())
            new_feat.setAttributes(f.attributes())
            new_features.append(new_feat)
            
        layer.addFeatures(new_features)
        layer.commitChanges()
        self.iface.mapCanvas().refresh()
        self.iface.messageBar().pushMessage("Success", f"Layer '{layer.name()}' reloaded successfully.", level=Qgis.Success)

    
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

    

    def save_to_csv(self):
        import csv
        layer = self.iface.activeLayer()
        if not layer:
            self.iface.messageBar().pushMessage("Warning", "Please select a layer to save.", level=Qgis.Warning)
            return

        original_delimiter = layer.customProperty('original_delimiter')
        original_x_field = layer.customProperty('original_x_field')
        original_y_field = layer.customProperty('original_y_field')
        original_file_path = layer.customProperty('original_file_path', '') # Provide a default value

        if not all([original_delimiter, original_x_field, original_y_field]):
            self.iface.messageBar().pushMessage("Error", "Cannot save: Original CSV properties not found for this layer.", level=Qgis.Critical)
            return

        file_name, _ = QFileDialog.getSaveFileName(self.iface.mainWindow(), "Save CSV File", original_file_path, "CSV Files (*.csv)")
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
