# config_panel.py
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget,
    QListWidgetItem, QSlider, QPushButton, QCheckBox, QHBoxLayout, QMenu
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from albionoverlay.gui.draggable_list import DraggableList

class ConfigPanel(QWidget):
    settings_changed = pyqtSignal(list, str, float, bool, list)

    def __init__(self, class_names):
        super().__init__()
        self.setWindowTitle("Overlay Settings")
        self.setGeometry(200, 200, 500, 600)

        layout = QVBoxLayout()

        # City selector
        layout.addWidget(QLabel("Market City:"))
        self.city_box = QComboBox()
        self.city_box.addItems(["Fort Sterling", "Bridgewatch", "Martlock", "Lymhurst", "Thetford", "Brecilien", "Caerleon", "Black Market"])
        layout.addWidget(self.city_box)

         # Confidence
        layout.addWidget(QLabel("Confidence Threshold:"))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(90)
        self.slider.setValue(30)
        layout.addWidget(self.slider)

        # Lists
        lists_layout = QHBoxLayout()

        self.available_list = DraggableList()
        self.available_list.setMinimumWidth(160)
        self.available_list.setDragDropMode(QListWidget.InternalMove)
        lists_layout.addWidget(self.create_labeled("Available Resources:", self.available_list))

        self.selected_list = DraggableList()
        self.selected_list.setMinimumWidth(160)
        self.selected_list.setDragDropMode(QListWidget.InternalMove)
        self.selected_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.selected_list.customContextMenuRequested.connect(self.handle_right_click)
        lists_layout.addWidget(self.create_labeled("Selected Resources:", self.selected_list))

        layout.addLayout(lists_layout)

        # Alerts
        self.alert_classes = set()

        # Fill selected list (by default all classes are selected)
        for cls in class_names:
            item = QListWidgetItem(cls)
            icon_path = os.path.join("resources", "icons", f"{cls}.png")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(pixmap))
            self.selected_list.addItem(item)

        # Overlay toggle
        self.toggle_overlay = QCheckBox("Show Overlay")
        self.toggle_overlay.setChecked(True)
        layout.addWidget(self.toggle_overlay)

        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.emit_settings)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def create_labeled(self, title, widget):
        wrapper = QVBoxLayout()
        wrapper.addWidget(QLabel(title))
        wrapper.addWidget(widget)
        container = QWidget()
        container.setLayout(wrapper)
        return container

    def emit_settings(self):
        selected = [self.selected_list.item(i).text() for i in range(self.selected_list.count())]
        city = self.city_box.currentText()
        conf = self.slider.value() / 100
        enabled = self.toggle_overlay.isChecked()
        self.settings_changed.emit(selected, city, conf, enabled, list(self.alert_classes))

    def handle_right_click(self, pos):
        item = self.selected_list.itemAt(pos)
        if item:
            class_name = item.text()
            menu = QMenu()
            toggle_action = menu.addAction("Toggle Alert for " + class_name)
            action = menu.exec_(self.selected_list.mapToGlobal(pos))
            if action == toggle_action:
                if class_name in self.alert_classes:
                    self.alert_classes.remove(class_name)
                    item.setBackground(Qt.white)
                else:
                    self.alert_classes.add(class_name)
                    item.setBackground(Qt.yellow)
