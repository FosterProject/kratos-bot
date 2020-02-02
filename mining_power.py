import matplotlib.pyplot as plt
from darkflow.net.build import TFNet
import numpy as np
import cv2
import time
import random

# Custom Library
import tools.image_lib as imlib
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos
from tools import config
import bot

# OSRS Specific
import inventory


# OSRS Constants
COPPER_REFERENCE = "bot_ref_imgs/copper.png"


# Window Constants (Used for an artificial (0,0) coord when translating click region back to screen)
TRANSLATION_DIST = ((config.SCREEN_HEIGHT / 2) - (config.SCREEN_HEIGHT / 15))
TRANSLATION_TOPLEFT = Pos((config.SCREEN_WIDTH / 2) - TRANSLATION_DIST, (config.SCREEN_HEIGHT / 2) - TRANSLATION_DIST)

# Analysis Threshold
THRESHOLD = 0.5

# Load TFNet
TFNET_OPTIONS = {
    "model": "cfg/yolo-kratos.cfg",
    "gpu": 1.0,
    "load": -1,
    "labels": "./classes.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)
TF_NET.load_from_ckpt()

# Timing
CURRENT_TIME = time.time()
def log_time(log_str):
    global CURRENT_TIME
    print("%s: %s" % (log_str, time.time() - CURRENT_TIME))
    CURRENT_TIME = time.time()




# Drawing Bounds
def boxing(original_image, predictions):
    new_image = np.copy(original_image)

    for result in predictions:
        top_x = result['topleft']['x']
        top_y = result['topleft']['y']

        bottom_x = result['bottomright']['x']
        bottom_y = result['bottomright']['y']

        confidence = result['confidence']
        label = result['label'] + " " + str(round(confidence, 3))

        if confidence > 0.3:
            new_image = cv2.rectangle(new_image, (top_x, top_y), (bottom_x, bottom_y), (255, 0, 0), 3)
            new_image = cv2.putText(new_image, label, (top_x, top_y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 230, 0), 1, cv2.LINE_AA)

    return new_image


def select_rock(selections):
    for rock in selections:
        if rock['confidence'] > THRESHOLD:
            return {"topleft": rock['topleft'], "bottomright": rock['bottomright']}, rock
    return None


def get_rock_click_pos(rock):
    # Center of bounding box
    center_x = (rock["bottomright"]["x"] - rock["topleft"]["x"]) / 2
    center_y = (rock["bottomright"]["y"] - rock["topleft"]["y"]) / 2

    center_upscaled = imlib.upscale(Pos(
        x=center_x,
        y=center_y
    ))
    topleft_upscaled = imlib.upscale(Pos(
        x=rock["topleft"]["x"],
        y=rock["topleft"]["y"]
    ))

    return Pos(
        x=TRANSLATION_TOPLEFT.x + topleft_upscaled.x + center_upscaled.x,
        y=TRANSLATION_TOPLEFT.y + topleft_upscaled.y + center_upscaled.y
    )


def mine_rock():
    # Image Processing
    img_path = grabber.grab_fullscreen(file_name="current", save=True)
    # img_path = "xcurrent.png"
    imlib.rescale(img_path).save('current.png')
    current_img = cv2.imread('current.png')

    # TFNet Call
    pred_start = time.time()
    predictions = TF_NET.return_predict(current_img)
    print("Prediction time: %s" % time.time() - pred_start)

    # Select a rock to mine
    rock,_ = select_rock(predictions)
    if rock is None:
        print("Couldn't find a rock...")
        exit()

    print("Rock found!")
    click_pos = get_rock_click_pos(rock)

    # Click the rock
    bot.click(click_pos)

    if config.DEBUG:
        fig, ax = plt.subplots(figsize = (20, 10))
        ax.imshow(boxing(current_img, predictions))
        plt.show()


if __name__ == "__main__":
    mine_counter = 0
    mine_counter_max = random.randint(2, 3)
    while True:
        # Drop
        if mine_counter >= mine_counter_max:
            print("Dropping all my shit!")
            inventory.drop(COPPER_REFERENCE)
            mine_counter = 0
            mine_counter_max = random.randint(2, 5)

        # Mine
        print("Mining a rock...")
        mine_rock()
        mine_counter += 1
        time.sleep(random.randint(6, 10))
