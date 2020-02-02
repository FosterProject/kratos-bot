from PIL import ImageGrab
from . import config
from .screen_pos import Pos

# Constants
MAP = {
    "TL": Pos(1527, 10),
    "BR": Pos(1879, 358)
}

INV = {
    "TL": Pos(1385, 442),
    "BR": Pos(1796, 1004)
}

INV_1 = {
    "TL": Pos(1414, 463),
    "BR": Pos(1496, 529)
}

INV_ICON = {
    "TL": Pos(1810, 430),
    "BR": Pos(1891, 513)
}


def grab_fullscreen(file_name="current", save=False):
    img = ImageGrab.grab(bbox=(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)).convert('RGB')
    if save:
        file_path = '%s.png' % file_name
        img.save(file_path)
        return file_path
    else:
        return img


def grab_region(file_name="undefined", screen_region=MAP, save=False):
    img = ImageGrab.grab(bbox=(screen_region["TL"].x, screen_region["TL"].y, screen_region["BR"].x, screen_region["BR"].y)).convert('RGB')
    if save:
        file_path = '%s.png' % file_name
        img.save(file_path)
        return file_path
    else:
        return img