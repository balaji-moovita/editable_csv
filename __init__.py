def classFactory(iface):
    from .editable_csv import EditableCSV
    return EditableCSV(iface)
