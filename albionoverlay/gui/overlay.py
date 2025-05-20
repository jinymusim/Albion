import mss
import cv2
import csv
import os
import numpy as np
from albionoverlay.detection.resouce_detector import Detector
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPainter, QFont, QColor
from typing import List
from albionoverlay.utils.utils import find_game_rect, get_price, iou


class Overlay(QWidget):
    def __init__(
            self,
            detector: Detector,
            select_classes: List[str]=None,
            capture_region=None
        ):
        super().__init__()
        self.detector = detector
        self.selected = select_classes  # e.g. ['T4_ORE','T4_WOOD']
        self.dets = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dets)
        self.timer.start(1000)

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

    def _load_icons(self, class_names):
        icons = {}
        for cls in class_names:
            icon_path = os.path.join("resources", "icons", f"{cls}.png")
            if os.path.exists(icon_path):
                icons[cls] = QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return icons

    def update_dets(self):
        if not self.visible:
            return
        
        self.setVisible(False) # To capture clean frame

        rect = find_game_rect()
        if not rect:
            self.setVisible(True)
            return
        
        left, top, right, bottom = rect
        width, height = right-left, bottom-top
        self.monitor_rect = rect
        self.setGeometry(left, top, width, height)


        # capture game region
        sct = mss.mss()
        shot = sct.grab({"left": left, "top": top, "width": width, "height": height})
        frame = np.array(shot)[:, :, :3]

        self.setVisible(True) # Restore visibility

        #cv2.imshow("Debug - Raw Frame", frame)

        raw_dets = self.detector.detect(frame, self.selected, self.conf_threshold)

        smoothed = []
        for det in raw_dets:
            x1, y1, x2, y2, conf, name = det
            matched = False
            for prev in self.prev_dets:
                px1, py1, px2, py2, _, pname = prev
                if name == pname and iou((x1, y1, x2, y2), (px1, py1, px2, py2)) > 0.5:
                    smoothed.append(prev)  # reuse previous box
                    matched = True
                    break
            if not matched:
                smoothed.append(det)

                # Update session counter and log
                self.session_counts[name] = self.session_counts.get(name, 0) + 1
                self.logger.writerow([name, f"{conf:.2f}", x1, y1, x2, y2])
                self.log_file.flush()

        self.prev_dets = smoothed
        self.dets = smoothed
        
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setFont(QFont('Arial',15,QFont.Bold))
        for x1,y1,x2,y2,conf,name in self.dets:
            p.setPen(QColor(255, 255, 0))
            p.drawRect(QRect(x1, y1, x2 - x1, y2 - y1))

            price = get_price(name, self.city)
            # Icon or fallback to text
            if name in self.icons:
                p.drawPixmap(x1, y1 - 42, self.icons[name])
                p.drawText(x1 + 42, y1 - 5, f"{price} ({self.city})")
            else:
                p.drawText(x1, y1 - 5, f"{name} {price} ({self.city})")
