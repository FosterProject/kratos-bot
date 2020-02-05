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
from utilities import bank

# from bots import mining
from bots import bowstringer

s = Session(0, 0)
s2 = Session(0, 1)

bank.find_booth(s2)