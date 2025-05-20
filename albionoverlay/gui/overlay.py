import mss
import csv
import os
import keyboard
import threading
from albionoverlay.detection.resouce_detector import Detector
from albionoverlay.detection.tracker import SimpleTracker
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QThread
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap
from albionoverlay.utils.utils import get_price, iou, find_game_rect
from albionoverlay.gui.detworker import DetectionWorker


class Overlay(QWidget):
    def __init__(
            self,
            detector: Detector,
            select_classes: list[str]=None,
            capture_region=None
        ):
        super().__init__()
        self.detector = detector
        self.selected = select_classes  # e.g. ['T4_ORE','T4_WOOD']
        self.dets = []

        self.monitor = capture_region or mss.mss().monitors[1]
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0,0,self.monitor['width'],self.monitor['height'])
        self.show()

        self.conf_threshold = 0.3
        self.city = "Fort Sterling"
        self.visible = True

        self.icons = self._load_icons(detector.class_names)

        self.session_counts = {}   # tracks per-class count
        self.prev_dets = []        # buffer for smoothing
        self.log_file = open(os.path.join("logging", "session_log.csv"), "w", newline="")
        self.logger = csv.writer(self.log_file)
        self.logger.writerow(["class", "conf", "x1", "y1", "x2", "y2"])

        self.thread = QThread()
        self.worker = DetectionWorker(
            self.detector,
            get_config=self.get_detection_config,
            get_region=self.get_capture_region,
            smooth_fn=self.smooth_detections
        )
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.handle_detections)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

        self._detection_enabled = True
        # Start global hotkey listener in separate thread
        threading.Thread(target=self._hotkey_loop, daemon=True).start()

        self.tracker = SimpleTracker()

    def _load_icons(self, class_names):
        icons = {}
        for cls in class_names:
            icon_path = os.path.join("resources", "icons", f"{cls}.png")
            if os.path.exists(icon_path):
                icons[cls] = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return icons

    def get_detection_config(self):
        return self.selected, self.conf_threshold

    def get_capture_region(self):
        return find_game_rect()  # or game region if refined

    def handle_detections(self, dets):
        self.dets = dets
        self.update()

    def smooth_detections(self, raw_dets):
        # raw_dets = [(x1,y1,x2,y2,conf,class)]
        tracked = self.tracker.update(raw_dets)

        for _, _, _, _, conf, name, _ in tracked:
            self.session_counts[name] = self.session_counts.get(name, 0) + 1
            # optionally log here

        return tracked

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setFont(QFont('Arial',15,QFont.Bold))
        for x1, y1, x2, y2, _, name, tid in self.dets:
            p.setPen(QColor(255, 255, 0))
            p.drawRect(QRect(x1, y1, x2 - x1, y2 - y1))

            price = get_price(name, self.city)
            # Icon or fallback to text
            if name in self.icons:
                p.drawPixmap(x1, y1 - 42, self.icons[name])
                p.drawText(x1 + 42, y1 - 5, f"{price} ({self.city}), (ID: {tid})")
            else:
                p.drawText(x1, y1 - 5, f"{name} {price} ({self.city}), (ID: {tid})")

    def _hotkey_loop(self):
        keyboard.add_hotkey("F1", self._toggle_overlay)
        keyboard.add_hotkey("F2", self._toggle_detection)
        keyboard.wait()  # blocks forever in thread


    def _toggle_overlay(self):
        self.visible = not self.visible
        self.setVisible(self.visible)
        print(f"[Overlay] Visibility set to {self.visible}")

    def _toggle_detection(self):
        self._detection_enabled = not self._detection_enabled
        self.worker.set_enabled(self._detection_enabled)
        print(f"[Detection] Running: {self._detection_enabled}")

