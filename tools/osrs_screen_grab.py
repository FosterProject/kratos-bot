from PIL import ImageGrab
from . import config
from .screen_pos import Pos, Box


# Constants
INVENTORY = Box(Pos(624, 196), Pos(804, 444))
MAP = Box(Pos(696, 8), Pos(841, 153))
BAR_RIGHT_TOP = Box(Pos(814, 194), Pos(844, 225))
BAR_LEFT_TOP = Box(Pos(2, 194), Pos(33, 225))
COMPASS = Box(Pos(682, 11), Pos(707, 29))
DRAG_BOUNDS = Box(Pos(66, 71), Pos(609, 392))

# INVENTORY
# items are 32 wide
# items are 28
# width between = 8
# height between = 6



def grab(bounding_box, region=None, file_name="default_grab", save=False):
    if region is not None:
        bounding_box.subdivision(region)
    img = ImageGrab.grab(bbox=(bounding_box.tl.x, bounding_box.tl.y, bounding_box.br.x, bounding_box.br.y)).convert('RGB')
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