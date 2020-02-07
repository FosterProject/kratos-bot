import sys
from PIL import ImageGrab

# Snips an inventory item sized image from the first inventory slot
# of the 0, 0 game client.

from tools.session import Session
s = Session(0, 0)

from tools import osrs_screen_grab as grabber
from utilities import inventory

pos = s.translate(grabber.INVENTORY_ITEM_FIRST_POS)

if len(sys.argv) == 2:
    img = ImageGrab.grab(bbox=(
        pos.x,
        pos.y,
        pos.x + inventory.ITEM_WIDTH,
        pos.y + inventory.ITEM_HEIGHT
    )).convert("RGB")

    img.save("bot_ref_imgs/%s.png" % sys.argv[1])
elif len(sys.argv) == 3:
    if sys.argv[1] == "short":
        img = ImageGrab.grab(bbox=(
            pos.x,
            pos.y + 9,
            pos.x + inventory.ITEM_WIDTH,
            pos.y + inventory.ITEM_HEIGHT
        )).convert("RGB")

        img.save("bot_ref_imgs/%s.png" % sys.argv[2])