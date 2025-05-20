import mss
import time
import uuid
import os
from albionoverlay.utils.utils import find_game_rect

while True:
    rect = find_game_rect()
    if not rect:
        continue
    left, top, right, bottom = rect
    width, height = right-left, bottom-top

    # capture game region
    sct = mss.mss()
    img = sct.grab({"left": left, "top": top, "width": width, "height": height})

    uuid_str = str(uuid.uuid4())
    mss.tools.to_png(img.rgb, img.size, output=os.path.join("logging", "screenshots", f"screen_{uuid_str}.png"))
    time.sleep(10)