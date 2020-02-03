from tools.session import Session
from tools import config
config.DEBUG = True
import pyautogui as bot

from bots import mining

import account
import ui

s = Session(0, 0)
s2 = Session(0, 1)
mining_bot = mining.Mining(s)