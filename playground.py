from tools.session import Session
from tools import osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import config
config.DEBUG = True
import pyautogui as bot

from bots import mining

from utilities import account
from utilities import ui

s = Session(0, 0)
s2 = Session(0, 1)


s.find_in_region(Box(
    grabber.INVENTORY_ITEM_FIRST_POS,
    Pos(
        grabber.INVENTORY_ITEM_FIRST_POS.x + 32,
        grabber.INVENTORY_ITEM_FIRST_POS.y + 32
    )
), "bot_ref_imgs/quad_1080/empty_test.png")
