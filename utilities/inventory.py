import time
import random

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
from tools.lib import file_name
from tools.event_manager import Event

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


def check_inventory(session, items, return_first=False):
    # Open the inventory
    ui.open_inventory(session)

    time_start = time.time()

    # Force into an array
    if not isinstance(items, list):
        items = [items]

    found = {}
    for item in items:
        exit_early = False
        found[item.reference] = []
        for x in range(0, 4):
            if exit_early: break
            for y in range(0, 7):
                if exit_early: break
                tl = Pos(
                    grabber.INVENTORY_ITEM_FIRST_POS.x + (x * ITEM_WIDTH) + (x * INVENTORY_BUFFER_WIDTH),
                    grabber.INVENTORY_ITEM_FIRST_POS.y + (y * ITEM_HEIGHT) + (y * INVENTORY_BUFFER_HEIGHT)
                )
                if item.has_unique_threshold(): session.set_region_threshold(item.threshold)
                find = session.find_in_region(Box(
                    tl,
                    Pos(tl.x + ITEM_WIDTH, tl.y + ITEM_HEIGHT)
                ), item.reference)

                if find is not None:
                    found[item.reference].append(find)
                    if return_first: exit_early = True
        debug("Inventory - check_inventory: %s [%s]" % (file_name(item.reference), len(found[item.reference])))

    debug("Inventory - check_inventory: check time = %s" % round(time.time() - time_start, 3))
    return found


def click_slot(session, slot):
    return session.translate(INVENTORY_POSITIONS[slot].random_point())


def has_amount(session, item, limit):
    found = check_inventory(session, item.reference)[item.reference]
    debug("Inventory - has_amount: Found: %s" % len(found))
    return len(found) >= limit


def drop(session, item):
    item_positions = check_inventory(session, item.reference)[item.reference]
    event = Event()
    for pos in item_positions:
        event.add_action(Event.click(pos), (.3, .75))
    session.publish_event(event)