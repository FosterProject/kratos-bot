import random
import time
import sys

from tools import config
from tools.screen_pos import Pos, Box
from tools import image_lib as imlib


def file_name(file_path):
    return file_path.split("/")[-1].split(".")[0]


def debug(debug_message):
    if config.DEBUG:
        print("DEBUG >> %s" % debug_message)


def error(error_message):
    print("Kratos-bot - ERROR >> %s" % error_message)


def pos_dist(pos1, pos2):
    x = abs(pos1.x - pos2.x)
    y = abs(pos1.y - pos2.y)
    if x < y:
        return (14 * x) + (10 * (y - x))
    else:
        return (14 * y) + (10 * (x - y))


def wait(min, max):
    length = random.uniform(min, max)
    time.sleep(length)


def translate_tracker(predictions, confidence=0.5):
    bbox_result = []
    predictions = [
        prediction for prediction in predictions if prediction["confidence"] > confidence]
    for prediction in predictions:
        topleft = Pos(
            x=prediction["topleft"]["x"],
            y=prediction["topleft"]["y"]
        )
        bottomright = Pos(
            x=prediction["bottomright"]["x"],
            y=prediction["bottomright"]["y"]
        )
        bbox_result.append((
            topleft.x,
            topleft.y,
            (bottomright.x - topleft.x),
            (bottomright.y - topleft.y)
        ))
    return bbox_result


def translate_predictions(predictions, return_as_box=False, confidence=0.5):
    bbox_result = []
    predictions = [
        prediction for prediction in predictions if prediction["confidence"] > confidence]
    for prediction in predictions:
        topleft = imlib.upscale(Pos(
            x=prediction["topleft"]["x"],
            y=prediction["topleft"]["y"]
        )).add(Pos(imlib.left, imlib.upper))
        bottomright = imlib.upscale(Pos(
            x=prediction["bottomright"]["x"],
            y=prediction["bottomright"]["y"]
        )).add(Pos(imlib.left, imlib.upper))
        if return_as_box:
            bbox_result.append(Box(topleft, bottomright))
        else:
            bbox_result.append((
                topleft.x,
                topleft.y,
                (bottomright.x - topleft.x),
                (bottomright.y - topleft.y)
            ))

    return bbox_result
