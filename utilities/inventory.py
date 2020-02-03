import cv2
import numpy as np
from matplotlib import pyplot as plt

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import bot
from tools import config
from tools import screen_search


# Constants
ITEM_WIDTH = 32
ITEM_HEIGHT = 32
INVENTORY_BUFFER_HEIGHT = 2
INVENTORY_BUFFER_WIDTH = 8

def build_inventory_positions():
    positions = []
    for y in range(0, 7):
        for x in range(0, 4):
            tl = Pos(
                grabber.INVENTORY_ITEM_FIRST_POS.x + (x * ITEM_WIDTH) + (x * INVENTORY_BUFFER_WIDTH),
                grabber.INVENTORY_ITEM_FIRST_POS.y + (y * ITEM_HEIGHT) + (y * INVENTORY_BUFFER_HEIGHT)
            )
            positions.append(Box(tl, Pos(tl.x + ITEM_WIDTH, tl.y + ITEM_HEIGHT)))
    return positions
INVENTORY_POSITIONS = build_inventory_positions()

# Utilities
from utilities import ui


def check_inventory(session, item_ref, return_positions=False):
    # Open the inventory
    ui.open_inventory(session)

    found = []
    for x in range(0, 4):
        for y in range(0, 7):
            tl = Pos(
                grabber.INVENTORY_ITEM_FIRST_POS.x + (x * ITEM_WIDTH) + (x * INVENTORY_BUFFER_WIDTH),
                grabber.INVENTORY_ITEM_FIRST_POS.y + (y * ITEM_HEIGHT) + (y * INVENTORY_BUFFER_HEIGHT)
            )
            find = session.find_in_region(Box(
                tl,
                Pos(tl.x + ITEM_WIDTH, tl.y + ITEM_HEIGHT)
            ), item_ref)

            if find is not None:
                found.append(session.translate(find))

    if return_positions:
        return len(found), found 
    else:
        return len(found), None


def has_amount(session, reference_image, limit):
    screen = grabber.grab(session)
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
        cv2.imwrite('debug/inventory_has_amount_outcome.png', _)
        
    return len(drawn) >= limit


def find(reference_img):
    pos = screen_search.find_in_region(grabber.INV, reference_img)
    if pos is not None:
        pos.add_raw(grabber.INV["TL"].x, grabber.INV["TL"].y)
    return pos


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