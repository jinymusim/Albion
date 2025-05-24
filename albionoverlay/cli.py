# albionoverlay/cli.py
import sys
import argparse
from albionoverlay.detection.resouce_detector import Detector
from PyQt5.QtWidgets import QApplication

from albionoverlay.gui.overlay import Overlay
from albionoverlay.gui.config_panel import ConfigPanel

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="Path to the model file")
    parser.add_argument("--data", required=True, help="Path to the data file")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    det = Detector(args.model,args.data,)
    ov = Overlay(detector=det, select_classes=det.class_names)

    config = ConfigPanel(det.class_names)

    def apply_settings(classes, city, conf, enabled, alert_list):
        ov.selected = classes
        ov.city = city
        ov.conf_threshold = conf
        ov.visible = enabled
        ov.alert_classes = set(alert_list)

    config.settings_changed.connect(apply_settings)
    config.show()

    sys.exit(app.exec_())
