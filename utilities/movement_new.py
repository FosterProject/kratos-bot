import cv2
import numpy as np
import time
import math

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Box, Pos
from tools import config
from tools import bot
from tools.lib import debug


# Image References
WORLD_MAP = "bot_ref_imgs/movement_new/world_map_varrock.png"

class Movement:
    def __init__(self, session):
        self.session = session

    
    def find_position_in_world_map(self):
        _ = cv2.imread(WORLD_MAP)
        screen = cv2.imread(WORLD_MAP, 0)

        template_box, template = self.get_world_map_portion()
        template = np.array(template.convert("L"))
        w = template_box.width
        h = template_box.height

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        maxpos = cv2.minMaxLoc(res)
        if maxpos[1] < 0.1:
            cv2.imwrite('debug/client%s%s/fail_find_in_world_map.png' % (self.session.row, self.session.col), _)
            debug("WORLD_MAP_SEARCH_ERROR")
            return None

        maxpos = cv2.minMaxLoc(res)[3]

        print(maxpos)
        print((maxpos[0] + (w / 2) - 1))

        if config.DEBUG:
            cv2.rectangle(_, maxpos, (maxpos[0] + int(w), maxpos[1] + int(h)), (255, 0, 0), 1)
            cv2.rectangle(_, (
                int(maxpos[0] + (w / 2)) + 2,
                int(maxpos[1] + (w / 2)) - 1
            ), (
                int(maxpos[0] + (w / 2)) + 2,
                int(maxpos[1] + (w / 2)) - 1
            ), (255, 0, 0), 1)
            cv2.imwrite('debug/client%s%s/find_in_world_map.png' % (self.session.row, self.session.col), _)

        return self.session.translate(Box(
            Pos(*maxpos),
            Pos(maxpos[0] + w, maxpos[1] + h)
        ).random_point())


    def get_world_map_portion(self):
        map_width = config.GAME_WIDTH - config.WORLD_MAP_X_BUFFER_LEFT - config.WORLD_MAP_X_BUFFER_RIGHT
        map_height = config.GAME_HEIGHT - config.WORLD_MAP_Y_BUFFER_TOP - config.WORLD_MAP_Y_BUFFER_BOTTOM
        cx = map_width / 2
        cy = map_height / 2
        dist = cx / 11 

        tl = Pos(
            (cx - dist) + config.WORLD_MAP_X_BUFFER_LEFT,
            (cy - dist) + config.WORLD_MAP_Y_BUFFER_TOP
        )
        inner_box = Box(
            tl,
            Pos(
                tl.x + (dist * 2),
                tl.y + (dist * 2)
            )
        )

        # return grabber.grab(self.session.screen_bounds, inner_box, "debug/maptest", True)
        return inner_box, grabber.grab(self.session.screen_bounds, inner_box)
