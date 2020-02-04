import time

import cv2
import numpy as np

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import bot
from tools import config
from tools import screen_search
from tools.lib import debug
from tools.lib import wait


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


def check_inventory(session, item_ref, return_first=False):
    # Open the inventory
    ui.open_inventory(session)

    time_start = time.time()

    # Force into an array
    if not isinstance(item_ref, list):
        item_ref = [item_ref]

    found = {}
    for ref in item_ref:
        exit_early = False
        found[ref] = []
        for x in range(0, 4):
            if exit_early: break
            for y in range(0, 7):
                if exit_early: break
                tl = Pos(
                    grabber.INVENTORY_ITEM_FIRST_POS.x + (x * ITEM_WIDTH) + (x * INVENTORY_BUFFER_WIDTH),
                    grabber.INVENTORY_ITEM_FIRST_POS.y + (y * ITEM_HEIGHT) + (y * INVENTORY_BUFFER_HEIGHT)
                )
                find = session.find_in_region(Box(
                    tl,
                    Pos(tl.x + ITEM_WIDTH, tl.y + ITEM_HEIGHT)
                ), ref)

                if find is not None:
                    found[ref].append(find)
                    if return_first: exit_early = True


    debug("Inventory: check time = %s" % round(time.time() - time_start, 3))
    return found


def has_amount(session, reference_image, limit):
    found = check_inventory(session, reference_image)[reference_image]
    debug("Inventory - has_amount: Found: %s" % len(found))
    return len(found) >= limit


def drop(session, reference_image):
    item_positions = check_inventory(session, reference_image)[reference_image]
    for pos in item_positions:
        bot.click(pos)
        wait(0.5, 0.75)