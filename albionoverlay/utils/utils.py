
# Windows-specific: find game window
import win32gui

def find_game_rect(window_title_substr: str = "Albion Online") -> tuple:
    hwnd = win32gui.FindWindow(None, None)
    # enumerate windows
    def callback(handle, ctx):
        if win32gui.IsWindowVisible(handle):
            title = win32gui.GetWindowText(handle)
            if window_title_substr.lower() in title.lower():
                ctx.append(handle)
    handles = []
    win32gui.EnumWindows(callback, handles)
    if not handles:
        return None
    rect = win32gui.GetWindowRect(handles[0])
    # rect: (left, top, right, bottom)
    return rect


import requests
import time
import os
import csv
from datetime import datetime

# Get item price from Albion Online API
_price_cache = {}
_CACHE_TIMEOUT = 300  # 5 minutes in seconds

# Log file
_PRICE_LOG_FILE = open(os.path.join("logging", "price_log.csv"), "a", newline="")
_price_logger = csv.writer(_PRICE_LOG_FILE)
if _PRICE_LOG_FILE.tell() == 0:
    _price_logger.writerow(["timestamp", "resource", "city", "price"])

def get_price(item_name: str, city: str = "Caerleon") -> str:
    key = (item_name, city)
    now = time.time()

    # Return cached value if not expired
    if key in _price_cache:
        cached_price, timestamp = _price_cache[key]
        if now - timestamp < _CACHE_TIMEOUT:
            return cached_price

    # Otherwise fetch from API
    try:
        url = f"https://www.albion-online-data.com/api/v2/stats/prices/{item_name}.json"
        r = requests.get(url, timeout=2)
        r.raise_for_status()
        data = r.json()
        for entry in data:
            if entry['city'] == city:
                price = entry['sell_price_min']
                price_str = f"{price:,}"
                _price_cache[key] = (price_str, now)

                # Log the fetch
                _price_logger.writerow([
                    datetime.utcnow().isoformat(),
                    item_name,
                    city,
                    price
                ])
                _PRICE_LOG_FILE.flush()
                return price_str
    except:
        pass

    return "N/A"


# Calculate Intersection over Union (IoU)
def iou(box1, box2):
    xa = max(box1[0], box2[0])
    ya = max(box1[1], box2[1])
    xb = min(box1[2], box2[2])
    yb = min(box1[3], box2[3])
    inter = max(0, xb - xa) * max(0, yb - ya)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0