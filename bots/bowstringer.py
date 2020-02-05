# Base session
from tools.session import Session

# Utilities
from utilities import account
from utilities.items import Item

# Image References
BOWSTRING = Item("bot_ref_imgs/quad_1080/fletching/bowstring.png", 0.32)
UNSTRUNG = Item("bot_ref_imgs/quad_1080/fletching/yew_unstrung.png", 0.33)
LONGBOW = Item("bot_ref_imgs/quad_1080/fletching/yew_longbow.png")

class Bowstringer:
    def __init__(self, session):
        self.session = session
