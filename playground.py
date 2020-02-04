from tools.session import Session
from tools import osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import config
config.DEBUG = True
import pyautogui as bot

from bots import mining
from bots import bowstringer

from utilities import account
from utilities import ui
from utilities import inventory

s = Session(0, 0)
# s2 = Session(0, 1)

# bot = mining.Mining(s)
# bot = bowstringer.Bowstringer(s)
# ui.open_inventory(s)

inventory.drop(s, mining.COPPER)