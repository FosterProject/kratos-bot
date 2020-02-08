import cv2
from PIL import ImageGrab
from . import config
from .screen_pos import Pos, Box


# Constants
PLAYER = Box(Pos(414, 228), Pos(452, 629))
LOGIN_BUTTON = Box(Pos(377, 231), Pos(463, 265))
LOBBY_BUTTON = Box(Pos(318, 274), Pos(526, 352))
LOGOUT_BUTTON = Box(Pos(652, 400), Pos(775, 420))

BANK = Box(Pos(125, 146), Pos(586, 459))
BANK_WITHDRAW_ALL = Box(Pos(417, 438), Pos(432, 450))
BANK_WITHDRAW_X = Box(Pos(394, 438), Pos(409, 450))
BANK_DEPOSIT_INVENTORY = Box(Pos(525, 434), Pos(542, 451))
BANK_CLOSE = Box(Pos(562, 155), Pos(576, 169))
BANK_ITEM_FIRST_POS = Pos(639, 203)

INVENTORY = Box(Pos(624, 196), Pos(804, 444))
INVENTORY_ITEM_FIRST_POS = Pos(639, 203)

MAP = Box(Pos(696, 8), Pos(841, 153))
COMPASS = Box(Pos(682, 11), Pos(707, 29))

TAP_OPTION = Box(Pos(5, 166), Pos(29, 181))
BAR_RIGHT_TOP = Box(Pos(815, 195), Pos(841, 221))
BAR_LEFT_TOP = Box(Pos(6, 197), Pos(29, 220))

DRAG_BOUNDS = Box(Pos(66, 71), Pos(609, 392))



def grab(bounding_box, region=None, file_name="default_grab", save=False):
    if region is not None:
        bounding_box = bounding_box.subdivision(region)
    img = ImageGrab.grab(bbox=(bounding_box.tl.x, bounding_box.tl.y, bounding_box.br.x, bounding_box.br.y))
    if save:
        file_path = '%s.png' % file_name
        img.save(file_path)
        return file_path
    else:
        return img


# Depricated if not using Session
def grab_fullscreen(file_name="current", save=False):
    img = ImageGrab.grab(bbox=(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)).convert('RGB')
    if save:
        file_path = '%s.png' % file_name
        img.save(file_path)
        return file_path
    else:
        return img

# Depricated if not using Session
def grab_region(file_name="undefined", screen_region=MAP, save=False):
    img = ImageGrab.grab(bbox=(screen_region["TL"].x, screen_region["TL"].y, screen_region["BR"].x, screen_region["BR"].y)).convert('RGB')
    if save:
        file_path = '%s.png' % file_name
        img.save(file_path)
        return file_path
    else:
        return img