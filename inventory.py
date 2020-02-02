import cv2
import numpy as np
from matplotlib import pyplot as plt

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos
import bot
from tools import config


def is_full(reference_image, limit):
    screen = grabber.grab_region("", grabber.INV)
    _ = np.array(screen)
    screen = np.array(screen.convert("L"))
    template = cv2.imread(reference_image, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    drawn = []
    for pt in zip(*loc[::-1]):
        check = [pos for pos in drawn if (-5 <= pos.x - pt[0] <= 5) and (-5 <= pos.y - pt[1] <= 5)]
        if len(check) > 0:
            continue
        drawn.append(Pos(pt[0], pt[1]))

        if config.DEBUG:
            cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
    if config.DEBUG:
        cv2.imwrite('debug/inventory_full_outcome.png', _)
        
    return len(drawn) >= limit


def drop(reference_image):
    inv = grabber.grab_region("current_inv", grabber.INV, True)
    inv = cv2.imread(inv)
    inv_gray = cv2.cvtColor(inv, cv2.COLOR_BGR2GRAY)
    copper_template = cv2.imread(reference_image, 0)

    w, h = copper_template.shape[::-1]

    res= cv2.matchTemplate(inv_gray, copper_template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    drawn = []
    for pt in zip(*loc[::-1]):
        check = [pos for pos in drawn if (-5 <= pos.x - pt[0] <= 5) and (-5 <= pos.y - pt[1] <= 5)]
        if len(check) > 0:
            continue
        drawn.append(Pos(pt[0], pt[1]))

        bot.click(Pos(
            grabber.INV["TL"].x + pt[0] + (w / 2),
            grabber.INV["TL"].y + pt[1] + (h / 2)
        ))

        if config.DEBUG:
            cv2.rectangle(inv, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
    if config.DEBUG:
        cv2.imwrite('debug/current_inv_outcome.png', inv)