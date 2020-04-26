import time
import random
import sys

import cv2
import numpy as np
from matplotlib import pyplot as plt
from darkflow.net.build import TFNet
import win32con

# Custom library
from tools import brain_lib
from tools.lib import wait
from tools.lib import debug as console
from tools.lib import file_name
from data import regions

# Utilities
from utilities import ui

# Load Darkflow
TFNET_OPTIONS = {
    "pbLoad": "brain_bank/yolo-kratos.pb",
    "metaLoad": "brain_bank/yolo-kratos.meta",
    "labels": "brain_bank/labels.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)

# Reference Images
BANK_BOOTH = {
    "NORTH": [
        "bot_ref_imgs/bank/north_bank_booth_1.png",
        "bot_ref_imgs/bank/north_bank_booth_2.png",
        "bot_ref_imgs/bank/north_bank_booth_3.png",
        "bot_ref_imgs/bank/north_bank_booth_4.png",
        "bot_ref_imgs/bank/north_bank_booth_5.png",
        "bot_ref_imgs/bank/north_bank_booth_6.png",
        "bot_ref_imgs/bank/north_bank_booth_7.png",
        "bot_ref_imgs/bank/north_bank_booth_8.png"
    ],
    "EAST": [
        "bot_ref_imgs/bank/east_bank_booth_1.png",
        "bot_ref_imgs/bank/east_bank_booth_2.png",
        "bot_ref_imgs/bank/east_bank_booth_3.png",
        "bot_ref_imgs/bank/east_bank_booth_4.png",
        "bot_ref_imgs/bank/east_bank_booth_5.png",
        "bot_ref_imgs/bank/east_bank_booth_6.png",
        "bot_ref_imgs/bank/east_bank_booth_7.png",
        "bot_ref_imgs/bank/east_bank_booth_8.png",
        "bot_ref_imgs/bank/east_bank_booth_9.png",
        "bot_ref_imgs/bank/east_bank_booth_10.png",
        "bot_ref_imgs/bank/east_bank_booth_11.png",
        "bot_ref_imgs/bank/east_bank_booth_12.png"
    ]
}
WITHDRAW_ALL_INACTIVE = "bot_ref_imgs/bank/withdraw_all_inactive.png"
WITHDRAW_X_INACTIVE = "bot_ref_imgs/bank/withdraw_x_inactive.png"
WITHDRAW_X_AMOUNT = "bot_ref_imgs/bank/withdraw_x_amount.png"
IS_BANK_OPEN = "bot_ref_imgs/bank/is_bank_open.png"


def bank_cycle(client, facing="NORTH", withdraw=[]):
    # Open bank
    while not is_bank_open(client):
        open(client, facing)
        wait(2, 5)

    # Bank inventory
    bank_inventory(client)
    wait(1, 3)

    # Withdraw items
    if isinstance(withdraw, list):
        for item in withdraw:
            withdraw_item(client, item)
    else:
        withdraw_item(client, withdraw)

    wait(1, 2)

    # Close
    close(client)


def is_select_x_inactive(client):
    check = client.set_threshold(.75).find(WITHDRAW_X_INACTIVE, regions.BANK)
    return check is not None


def is_select_all_inactive(client):
    check = client.set_threshold(.93).find(WITHDRAW_ALL_INACTIVE, regions.BANK)
    return check is not None


def options_select_all(client):
    if is_select_all_inactive(client):
        console("BANK: Selecting 'withdraw all'")

        client.click(regions.BANK_WITHDRAW_ALL.random_point())


def options_select_x(client):
    if is_select_x_inactive(client):
        console("BANK: Selecting 'withdraw x'")

        # Click withdraw x
        client.click(regions.BANK_WITHDRAW_X.random_point())

        # Check if amount menu pops up
        check = client.find(WITHDRAW_X_AMOUNT)
        if check is not None:
            client.key(0x31)  # 1
            client.key(0x34)  # 4
            client.key(win32con.VK_RETURN)


def bank_inventory(client):
    client.click(regions.BANK_DEPOSIT_INVENTORY.random_point())


def find_item(client, item):
    if item.has_unique_threshold():
        client.set_threshold(item.threshold)
    return client.find(item.reference, regions.BANK)


def withdraw_item(client, item):
    console("BANK - withdraw_item: %s" % file_name(item.reference))
    click_pos = find_item(client, item)
    if click_pos is None:
        console(
            "BANK - withdraw_item: Couldn't find item [%s]. Item is not in bank view." % file_name(item.reference))
        return
    # Already translated due to find_in_region
    client.click(click_pos)


def is_bank_open(client):
    check = client.set_threshold(.6).find(IS_BANK_OPEN, regions.BANK)
    return check is not None


def find_booth(client, facing="NORTH"):
    booth_found = False
    for booth in BANK_BOOTH[facing]:
        check = client.set_threshold(.75).find(booth)
        if check is not None:
            booth_found = True
            break

    if not booth_found:
        console("BANK - find_booth: Couldn't find bank booth in client")
        return None

    return check


def close(client):
    console("BANK - close: Closing the bank")
    if is_bank_open(client):
        client.click(regions.BANK_CLOSE.random_point())


def open_old(client, facing="NORTH"):
    attempts = 0
    booth_pos = None
    while booth_pos is None:
        if attempts >= 3:
            client.log(
                "BANK - open: Couldn't open the bank. Script is exiting because you're not in a bank.")
            sys.exit()
        attempts += 1
        booth_pos = find_booth(client, facing)
        if booth_pos is None:
            ui.click_compass(client)
            wait(.3, .5)

    client.click(booth_pos)

def open(client):
    attempts = 0
    while True:
        if is_bank_open(client):
            break
        if attempts >= 4:
            client.log("Couldn't find the bank. Exiting thread")
            sys.exit()
        frame = brain_lib.get_frame_for_brain(client.host)
        predictions = TF_NET.return_predict(frame)
        bboxes = brain_lib.translate_predictions(predictions, should_upscale=True, return_as_box=True)
        if len(bboxes) > 0:
            attempts += 1
            client.log("bank booth found")
            bank_pos = bboxes[0].center()
            client.click(bank_pos)
            
            waits = 0
            fail = False
            while not is_bank_open(client):
                if waits >= 6:
                    fail = True
                    break
                waits += 1
                wait(1, 2)
            if not fail:
                break
        else:
            client.log("spinning")
            ui.spin_around(client)
            wait(1, 1.5)