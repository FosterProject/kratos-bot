import cv2
import numpy as np
import random
import time

# Custom library
from tools.screen_pos import Pos, Box
from tools.lib import debug
from tools import screen_search
import bot

# Utilities
import ui


# Constants
LOGIN_BUTTON = Box(Pos(325, 223), Pos(516, 274))
LOBBY_BUTTON = Box(Pos(721, 625), Pos(1187, 795))
LOGOUT_BUTTON = Box(Pos(1452, 911), Pos(1731, 952))

# Images
LOGOUT_CHECK = "bot_ref_imgs/quad_1080/account/logout_check.png"
TAP_TO_PLAY = "bot_ref_imgs/account/tap_to_play.png"
CONNECTING_CHECK = "bot_ref_imgs/account/connecting_check.png"


def is_logged_out(session):
    check = session.find_in_client(LOGOUT_CHECK)
    return check is not None


def is_in_lobby(session):
    check = session.find_in_client(TAP_TO_PLAY)
    return check is not None


def is_connecting(session):
    check = session.find_in_client(CONNECTING_CHECK)
    return check is None


def login(session):
    if not is_logged_out(session):
        debug("Account: Already logged in")
        return

    debug("Logging in...")

    # Click login
    bot.click(LOGIN_BUTTON.random_point())

    # Enter game
    while not is_in_lobby(session):
        time.sleep(2)
        # If connection failed
        if not is_connecting(session):
            # Log in again
            bot.click(LOGIN_BUTTON.random_point())
    
    # Enter through lobby
    bot.click(LOBBY_BUTTON.random_point())


def logout(session):
    if is_logged_out():
        print("Already logged out you plum")
        return
    
    click_pos = screen_search.find_in_screen("bot_ref_imgs/account/logout_inactive.png")
    if click_pos is not None:
        bot.click(click_pos)

    time.sleep(random.randint(1, 2))

    # Click logout button
    bot.click(LOGOUT_BUTTON.random_point())
