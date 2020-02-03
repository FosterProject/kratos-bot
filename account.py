import cv2
import numpy as np
import random
import time

# Custom library
from tools.screen_pos import Pos, Box
import bot
from tools import config
from tools import screen_search


# Constants
LOGIN_BUTTON = Box(Pos(739, 509), Pos(1169, 619))
LOBBY_BUTTON = Box(Pos(721, 625), Pos(1187, 795))
LOGOUT_BUTTON = Box(Pos(1452, 911), Pos(1731, 952))

def is_logged_out():
    check = screen_search.find_in_screen("bot_ref_imgs/account/logout_check.png")
    return check is not None


def is_in_lobby():
    check = screen_search.find_in_screen("bot_ref_imgs/account/tap_to_play.png")
    return check is not None


def is_connecting():
    check = screen_search.find_in_screen("bot_ref_imgs/account/connecting_check.png")
    return check is None


def login():
    if not is_logged_out():
        print("Already logged in you plum")
        return

    print("Logging in...")

    # Click login
    bot.click(LOGIN_BUTTON.random_point())

    # Enter game
    while not is_in_lobby():
        time.sleep(2)
        # If connection failed
        if not is_connecting():
            # Log in again
            bot.click(LOGIN_BUTTON.random_point())
    
    # Enter through lobby
    bot.click(LOBBY_BUTTON.random_point())


def logout():
    if is_logged_out():
        print("Already logged out you plum")
        return
    
    click_pos = screen_search.find_in_screen("bot_ref_imgs/account/logout_inactive.png")
    if click_pos is not None:
        bot.click(click_pos)

    time.sleep(random.randint(1, 2))

    # Click logout button
    bot.click(LOGOUT_BUTTON.random_point())
