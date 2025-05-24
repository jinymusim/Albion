# Albion Overlay

Albion Overlay is a desktop application that provides a real-time overlay for the game Albion Online. It uses object detection to identify in-game resources and displays relevant information on top of the game window. The overlay is highly configurable and supports custom models and data files.

## Features

- Real-time detection of in-game resources using ONNX models
- Overlay display with PyQt5, always on top and frameless
- Configurable detection classes, confidence threshold, and city selection
- Session tracking and per-class resource counts
- Easy-to-use configuration panel

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/jinymusim/Albion.git
   cd Albion
   ```
2. **Installetion**
    ```sh
    pip install -e .
    ```

## Usage 
Run the overlay with default model
```sh
albion-overlay --model models/best.onnx --data data.yaml
```

- --model: Path to the ONNX model file for detection.
- --data: Path to the data file (YAML) describing class names and other metadata.

## Project Structure

- albionoverlay/cli.py: Command-line entry point.
- albionoverlay/gui/overlay.py: Overlay window implementation.
- albionoverlay/gui/config_panel.py: Configuration panel for user settings.
- albionoverlay/detection/resouce_detector.py: Resource detection logic.
- albionoverlay/utils/utils.py: Utility functions.
- models/: Pretrained models (e.g., best.onnx).
- resources/icons: Display icons for the different resources

## Development
- Requires Python 3.10 or higher.
- Main dependencies: PyQt5, OpenCV, onnxruntime, numpy, mss, requests, pyyaml.
- See requirements.txt for the full list.

## License
This project is licensed under the MIT License. See LICENSE.md for details.

## Author
Michal Chudoba