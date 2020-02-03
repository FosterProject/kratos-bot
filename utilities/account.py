import cv2
import numpy as np
import random
import time

# Custom library
from tools.screen_pos import Pos, Box
from tools.lib import debug
from tools.lib import wait
from tools import screen_search
from tools import osrs_screen_grab as grabber
from tools import bot

# Utilities
from utilities import ui

# Images
LOGOUT_CHECK = "bot_ref_imgs/quad_1080/account/logout_check.png"
TAP_TO_PLAY = "bot_ref_imgs/quad_1080/account/tap_to_play.png"
CONNECTING_CHECK = "bot_ref_imgs/quad_1080/account/connecting_check.png"
LOGOUT_INACTIVE = "bot_ref_imgs/quad_1080/account/logout_inactive.png"


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
    bot.click(session.translate(grabber.LOGIN_BUTTON.random_point()))

    # Enter game
    while not is_in_lobby(session):
        wait(1.5, 2)
        # If connection failed
        if not is_connecting(session):
            # Log in again
            bot.click(session.translate(grabber.LOGIN_BUTTON.random_point()))
    
    # Enter through lobby
    bot.click(session.translate(grabber.LOBBY_BUTTON.random_point()))


def logout(session):
    if is_logged_out(session):
        debug("Account: Already logged out you plum")
        return
    
    click_pos = session.find_in_client(LOGOUT_INACTIVE)
    if click_pos is not None:
        debug("Account: Opening logout tab")
        ui.open_tab(session, "RIGHT", 6)

    wait(1, 2)

    # Click logout button
    bot.click(session.translate(grabber.LOGOUT_BUTTON.random_point()))
