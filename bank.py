import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import random
import sys

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos
import bot
from tools import config


BANK_BOOTH = [
    "bot_ref_imgs/banking/bank_booth.png",
    "bot_ref_imgs/banking/bank_booth_2.png"
]


def bank_cycle(withdraw=[]):
    print(withdraw)
    # Open bank
    while not is_bank_open():
        open()
        time.sleep(random.randint(2, 5))
    
    # Bank inventory
    bank_inventory()
    time.sleep(random.randint(1, 3))

    # Withdraw items
    if isinstance(withdraw, list):
        for item in withdraw:
            withdraw_item(item)
    else:
        withdraw_item(withdraw)

    time.sleep(random.randint(1, 2))

    # Close
    close()


def find_close():
    screen = grabber.grab_fullscreen()
    _ = np.array(screen)
    screen = np.array(screen.convert("L"))
    template = cv2.imread("bot_ref_imgs/banking/close_bank.png", 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    if len(list(zip(*loc[::-1]))) < 1:
        print("Couldn't find close bank... fuck.")
        sys.exit()
    
    for pt in zip(*loc[::-1]):
        if config.DEBUG:
            cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
            cv2.imwrite('debug/close_bank_outcome.png', _)
        
        return Pos(
            pt[0] + (w / 2),
            pt[1] + (h / 2)
        )


def find_bank_inventory():
    screen = grabber.grab_fullscreen()
    _ = np.array(screen)
    screen = np.array(screen.convert("L"))
    template = cv2.imread("bot_ref_imgs/banking/bank_inventory.png", 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    if len(list(zip(*loc[::-1]))) < 1:
        print("Couldn't find bank inventory... fuck.")
        sys.exit()
    
    for pt in zip(*loc[::-1]):
        if config.DEBUG:
            cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
            cv2.imwrite('debug/bank_inventory_outcome.png', _)
        
        return Pos(
            pt[0] + (w / 2),
            pt[1] + (h / 2)
        )


def bank_inventory():
    # Bank inventory
    click_pos = find_bank_inventory()
    bot.click(click_pos)


def find_item(item_ref):
    screen = grabber.grab_fullscreen()
    _ = np.array(screen)
    screen = np.array(screen.convert("L"))
    template = cv2.imread(item_ref, 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    if len(list(zip(*loc[::-1]))) < 1:
        print("Couldn't find item in bank... fuck.")
        sys.exit()
    
    for pt in zip(*loc[::-1]):
        if config.DEBUG:
            cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
            cv2.imwrite('debug/withdraw_item_outcome.png', _)
        
        return Pos(
            pt[0] + (w / 2),
            pt[1] + (h / 2)
        )


def withdraw_item(item_ref):
    print("Withdrawing: %s" % item_ref)
    click_pos = find_item(item_ref)
    bot.click(click_pos)


def is_bank_open():
    screen = grabber.grab_fullscreen()
    _ = np.array(screen)
    screen = np.array(screen.convert("L"))
    template = cv2.imread("bot_ref_imgs/banking/open_bank.png", 0)
    w, h = template.shape[::-1]

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    if len(list(zip(*loc[::-1]))) > 0:
        return True
    else:
        return False


def find_booth():
    screen = grabber.grab_fullscreen()
    _ = np.array(screen)
    screen = np.array(screen.convert("L"))

    booth_found = False
    for booth in BANK_BOOTH:
        booth_template = cv2.imread(booth, 0)

        w, h = booth_template.shape[::-1]

        res = cv2.matchTemplate(screen, booth_template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if len(list(zip(*loc[::-1]))) > 0:
            booth_found = True
            break

    if not booth_found:
        print("Couldn't find bank booth... fuck.")
        sys.exit()
    
    for pt in zip(*loc[::-1]):
        if config.DEBUG:
            cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
            cv2.imwrite('debug/booth_outcome.png', _)
        
        return Pos(
            pt[0] + (w / 2),
            pt[1] + (h / 2)
        )
    

def close():
    click_pos = find_close()
    bot.click(click_pos)


def open():
    booth = find_booth()
    bot.click(booth)