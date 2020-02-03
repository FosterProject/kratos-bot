from tools.session import Session
from tools import osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import config
config.DEBUG = True
import pyautogui as bot

from bots import mining

from utilities import account
from utilities import ui
from utilities import inventory

s = Session(0, 0)
s2 = Session(0, 1)

bot = mining.Mining(s)
# ui.open_inventory(s)

x = inventory.check_inventory(s, "bot_ref_imgs/quad_1080/fletching/bowstring.png")
print(x)