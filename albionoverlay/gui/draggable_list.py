
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt


class DraggableList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.SingleSelection)

    def dragEnterEvent(self, event):
        if event.mimeData():
            event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        source = event.source()
        if source is not self:
            item = source.currentItem()
            source.takeItem(source.row(item))
            self.addItem(item.clone())
        event.accept()