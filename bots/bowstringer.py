# Base session
from tools.session import Session

# Utilities
from utilities import account

# Image References
BOWSTRING = "bot_ref_imgs/quad_1080/fletching/bowstring.png"
UNSTRUNG = "bot_ref_imgs/quad_1080/fletching/maple_unstrung.png"
LONGBOW = "bot_ref_imgs/quad_1080/fletching/maple_longbow.png"

class Bowstringer:
    def __init__(self, session):
        self.session = session
