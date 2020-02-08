import time
import random
import sys
import matplotlib.pyplot as plt
import numpy as np
import cv2
from darkflow.net.build import TFNet

# Custom Library
import tools.image_lib as imlib
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos
from tools import config
from tools import bot

# OSRS Specific
import inventory
import movement
import bank
import ui
import account


# OSRS Constants
COPPER_REFERENCE = "bot_ref_imgs/mining/copper.png"
PICKAXE_REFERENCE = "bot_ref_imgs/mining/pickaxe_mithril.png"


# Window Constants (Used for an artificial (0,0) coord when translating click region back to screen)
TRANSLATION_DIST = ((config.SCREEN_HEIGHT / 2) - (config.SCREEN_HEIGHT / 15))
TRANSLATION_TOPLEFT = Pos(
    (config.SCREEN_WIDTH / 2) - TRANSLATION_DIST,
    (config.SCREEN_HEIGHT / 2) - TRANSLATION_DIST
)

# Analysis Threshold
THRESHOLD = 0.8

# Load TFNet
TFNET_OPTIONS = {
    "model": "cfg/yolo-kratos.cfg",
    # "gpu": 1.0,
    "load": -1,
    "labels": "./classes.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)
TF_NET.load_from_ckpt()



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
    if len(selections) < 1:
        return None, None
    # sel = random.randint(0, len(selections) - 1)
    selections.sort(key=lambda x: float(x["confidence"]))
    rock = selections[0]
    return {"topleft": rock['topleft'], "bottomright": rock['bottomright']}, rock


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
    bottomright_upscaled = imlib.upscale(Pos(
        x=rock["bottomright"]["x"],
        y=rock["bottomright"]["y"]
    ))

    # return Pos.random(
    #     Pos(
    #         TRANSLATION_TOPLEFT.x + topleft_upscaled.x,
    #         TRANSLATION_TOPLEFT.y + topleft_upscaled.y
    #     ).scale(1.2).to_int(),
    #     Pos(
    #         TRANSLATION_TOPLEFT.x + bottomright_upscaled.x,
    #         TRANSLATION_TOPLEFT.y + bottomright_upscaled.y
    #     ).scale(0.8).to_int()
    # )

    return Pos(
        x=TRANSLATION_TOPLEFT.x + topleft_upscaled.x + center_upscaled.x,
        y=TRANSLATION_TOPLEFT.y + topleft_upscaled.y + center_upscaled.y
    )


def find_rocks():
    # Image Processing
    img_path = grabber.grab_fullscreen(file_name="current", save=True)
    imlib.rescale(img_path).save('current.png')
    current_img = cv2.imread('current.png')

    # TFNet Call
    pred_start = time.time()
    predictions = TF_NET.return_predict(current_img)
    print("Prediction time: %s" % int(time.time() - pred_start))

    if config.DEBUG:
        fig, ax = plt.subplots(figsize = (20, 10))
        ax.imshow(boxing(current_img, predictions))
        plt.show()

    return [rock for rock in predictions if float(rock["confidence"]) > THRESHOLD]


def mine_rock():
    # Find rocks using ML
    rocks = find_rocks()

    # Select a rock to mine
    rock,_ = select_rock(rocks)
    while rock is None:
        print("Couldn't find a rock...")
        ui.spin_around()
        rocks = find_rocks()
        rock,_ = select_rock(rocks)

    print("Rock found!")
    click_pos = get_rock_click_pos(rock)

    # Click the rock
    bot.click(click_pos)


def is_in_mine():
    success,_,_,_ = movement.analyse_map("bot_ref_imgs/mining/in_mine_check.png")
    return success


if __name__ == "__main__":
    # Bot pre-checks
    ################

    # Log in
    account.login()
    time.sleep(random.randint(3, 6))

    # Check if starting in the mine
    if not is_in_mine():
        print("You're not in the mine you pisshead. Start again when in the mine.")
        sys.exit()

    # Open inventory
    ui.open_inventory()

    # Start mining loop
    while True:
        # Mine until full
        while not inventory.has_amount(COPPER_REFERENCE, 24):
            # Mine
            print("Mining a rock...")
            mine_rock()
            time.sleep(random.randint(6, 10))

        # Move to bank
        ui.click_compass()
        movement.bank_path()
        time.sleep(random.randint(1, 4))

        # Bank invent
        bank.bank_cycle(withdraw=PICKAXE_REFERENCE)
        time.sleep(random.randint(1, 4))

        # Walk back to mine
        movement.bank_path(True)
        time.sleep(random.randint(1, 4))

        # Rotate camera
        ui.click_compass()
        ui.spin_around()
