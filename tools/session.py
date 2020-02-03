import cv2
import numpy as np


# Custom Library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import config


class Session:
    def __init__(self, row, col):
        # Screen position details
        self.row = row
        self.col = col
        tl = Pos(
            0 + (self.col * config.GAME_WIDTH) + (self.col * config.PADDING_LEFT) + (self.col * config.PADDING_RIGHT) + config.PADDING_LEFT,
            0 + (self.row * config.GAME_HEIGHT) + (self.row * config.PADDING_TOP) + (self.row * config.PADDING_BOTTOM) + config.PADDING_TOP
        )
        self.screen_bounds = Box(
            tl,
            Pos(
                tl.x + config.GAME_WIDTH,
                tl.y + config.GAME_HEIGHT
            )
        )
    

    def find_in_region(self, region, item_ref):
        screen = grabber.grab(self.screen_bounds, region)
        _ = np.array(screen)
        screen = np.array(screen.convert("L"))
        template = cv2.imread(item_ref, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if len(list(zip(*loc[::-1]))) < 1:
            if config.DEBUG: print("REGION_SEARCH_ERROR - [%s]: %s" % (region, item_ref))
            return None
        
        for pt in zip(*loc[::-1]):
            if config.DEBUG:
                cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
                cv2.imwrite('debug/region_%s.png' % item_ref.split("/")[-1].split(".")[0], _)
            
            return self.translate(Pos(
                pt[0] + (w / 2),
                pt[1] + (h / 2)
            ))


    def find_in_client(self, item_ref):
        screen = grabber.grab(self.screen_bounds)
        _ = np.array(screen)
        screen = np.array(screen.convert("L"))
        template = cv2.imread(item_ref, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        if len(list(zip(*loc[::-1]))) < 1:
            if config.DEBUG: print("CLIENT_SEARCH_ERROR: %s" % item_ref)
            return None
        
        for pt in zip(*loc[::-1]):
            if config.DEBUG:
                cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
                cv2.imwrite('debug/client%s%s/screen_%s.png' % (self.row, self.col, item_ref.split("/")[-1].split(".")[0]), _)
            
            return self.translate(Pos(
                pt[0] + (w / 2),
                pt[1] + (h / 2)
            ))
        

    def translate(self, pos):
        return pos.add(self.screen_bounds.tl)
