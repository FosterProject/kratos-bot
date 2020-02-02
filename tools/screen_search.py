import cv2
import numpy as np


# Custom Library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos
from tools import config



def find_in_screen(item_ref):
    screen = grabber.grab_fullscreen()
    _ = np.array(screen)
    screen = np.array(screen.convert("L"))
    template = cv2.imread(item_ref, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    if len(list(zip(*loc[::-1]))) < 1:
        print("Couldn't find item on screen... fuck.")
        return None
    
    for pt in zip(*loc[::-1]):
        if config.DEBUG:
            cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
            cv2.imwrite('debug/screen_search_outcome.png', _)
        
        return Pos(
            pt[0] + (w / 2),
            pt[1] + (h / 2)
        )