from os import walk
from PIL import Image
from .screen_pos import Pos
from . import config


# Calcs
cx = config.GAME_WIDTH / 2
cy = config.GAME_HEIGHT / 2
y_offset = config.GAME_HEIGHT / 15
dist = cy - y_offset

# Bounds
left = cx - dist
upper = cy - dist
right = cx + dist
lower = cy + dist


def rescale(image_path):
    # Load
    img = Image.open(image_path)

    # Crop
    cimg = img.crop((left, upper, right, lower))

    # Rescale
    wpercent = (config.SCALE_WIDTH / float(right - left))
    hsize = int((float(lower - upper) * float(wpercent)))
    img_scaled = cimg.resize((config.SCALE_WIDTH, hsize), Image.ANTIALIAS)

    return img_scaled


def rescale_obj(img_obj):
    # Crop
    cimg = img_obj.crop((left, upper, right, lower))

    # Rescale
    wpercent = (config.SCALE_WIDTH / float(right - left))
    hsize = int((float(lower - upper) * float(wpercent)))
    img_scaled = cimg.resize((config.SCALE_WIDTH, hsize), Image.ANTIALIAS)

    return img_scaled


def upscale(pos):
    # Rescale
    wpercent = (config.SCALE_WIDTH / float(right - left))
    hsize = int((float(lower - upper) * float(wpercent)))

    x_ratio = pos.x / config.SCALE_WIDTH
    y_ratio = pos.y / hsize
    return Pos(
        x=(right - left) * x_ratio,
        y=(lower - upper) * y_ratio
    )