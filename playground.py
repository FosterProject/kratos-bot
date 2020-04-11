from tools.session import Session
from tools import osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import image_lib as imlib
from tools.lib import translate_predictions
from tools import config
from utilities.items import Item
config.DEBUG = True
import pyautogui as bot

import time

# from bots import mining
# from bots import bowstringer

from utilities import account
from utilities import ui
from utilities import inventory
from utilities import bank


s = Session(0, 0)
# s2 = Session(0, 1)

# screen = grabber.grab(s.screen_bounds, grabber.CHAT_LAST_LINE, "debug/test.png", True)

# from darkflow.net.build import TFNet
# import cv2
# import numpy as np
# TFNET_OPTIONS = {
#     "pbLoad": "brain_tanner/yolo-kratos.pb",
#     "metaLoad": "brain_tanner/yolo-kratos.meta",
#     "labels": "./labels.txt",
#     "threshold": 0.1
# }
# TF_NET = TFNet(TFNET_OPTIONS)



# x = s.set_region_threshold(0.6).find_in_region(grabber.MAP, "bot_ref_imgs/tanner/movement/1.png")
# x = bank.find_booth(s, "EAST")
# print(x)