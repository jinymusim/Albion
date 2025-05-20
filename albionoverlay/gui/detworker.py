from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np
import time
import mss

class DetectionWorker(QObject):
    finished = pyqtSignal(list)
    
    def __init__(self, detector, get_config, get_region, smooth_fn):
        super().__init__()
        self.detector = detector
        self.get_config = get_config
        self.get_region = get_region
        self.smooth_fn = smooth_fn
        self._running = True
        self._enabled = True 

    def stop(self):
        self._running = False
    
    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def run(self):
        sct = mss.mss()
        while self._running:
            if not self._enabled:
                time.sleep(0.01)
                continue

            region = self.get_region()
            if region is None:
                time.sleep(0.01)
                continue

            shot = sct.grab(region)
            frame = np.array(shot)[:, :, :3]

            selected, threshold = self.get_config()
            raw_dets = self.detector.detect(frame, selected, threshold)
            smoothed = self.smooth_fn(raw_dets)
            self.finished.emit(smoothed)

            time.sleep(0.01)
