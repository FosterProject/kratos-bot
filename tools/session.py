import time
import random

import cv2
import numpy as np

# Event Manager
from tools.event_manager import EventManager
EM = EventManager.get_instance()

# Custom Library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import config
from tools.lib import debug
from tools.lib import file_name
from tools.lib import wait


class Session:
    def __init__(self, row, col):
        # Thread safety
        self._exit_thread = False

        # EventManager
        self.has_pending_event = False

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

        # Thresholds
        self.region_threshold = 0.3
        self.client_threshold = 0.8

        # Timers
        self._login_time = time.time()
        self._login_time_max = 300 * 60


    def exit(self):
        self._exit_thread = True


    def should_exit(self):
        return self._exit_thread


    def publish_event(self, event):
        EM.add_event(self, event)
        while self.has_pending_event and not self._exit_thread:
            wait(.5, 1)

    # NOT WORKING PROPERLY
    def find_in_region_colour(self, region, item_ref):
        screen = grabber.grab(self.screen_bounds, region)
        screen = cv2.cvtColor(np.array(screen), cv2.COLOR_BGR2RGB)
        template = cv2.imread(item_ref)
        cv2.imwrite('debug/client%s%s/region_colour_template_%s.png' % (self.row, self.col, file_name(item_ref)), template)
        h = template.shape[0]
        w = template.shape[1]
        template = cv2.cvtColor(np.array(template), cv2.COLOR_BGR2RGB)

        res = cv2.ximgproc.colorMatchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= self.region_threshold)
        self.reset_region_threshold()
        if len(list(zip(*loc[::-1]))) < 1:
            cv2.rectangle(screen, (region.tl.x, region.tl.y), (region.br.x, region.br.y), (25, 0, 255), 2)
            cv2.imwrite('debug/client%s%s/fail_region_colour_%s.png' % (self.row, self.col, file_name(item_ref)), screen)
            debug("REGION_SEARCH_ERROR - [%s]: %s" % (region, item_ref))
            return None

        for pt in zip(*loc[::-1]):
            if config.DEBUG:
                cv2.rectangle(screen, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
                cv2.imwrite('debug/client%s%s/region_colour_%s.png' % (self.row, self.col, file_name(item_ref)), screen)
            
            return self.translate(Box(
                Pos(*pt),
                Pos(pt[0] + w, pt[1] + h)
            ).random_point(), region)


    def find_in_region(self, region, item_ref):
        screen = grabber.grab(self.screen_bounds, region)
        _ = np.array(screen)
        screen = np.array(screen.convert("L"))
        template = cv2.imread(item_ref, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        maxpos = cv2.minMaxLoc(res)
        if maxpos[1] < self.region_threshold:
            cv2.rectangle(_, (region.tl.x, region.tl.y), (region.br.x, region.br.y), (25, 0, 255), 2)
            cv2.imwrite('debug/client%s%s/fail_region_%s.png' % (self.row, self.col, file_name(item_ref)), _)
            debug("REGION_SEARCH_ERROR - [%s]: %s" % (region, item_ref))
            return None

        self.reset_region_threshold()
        maxpos = cv2.minMaxLoc(res)[3]

        return self.translate(Box(
            Pos(*maxpos),
            Pos(maxpos[0] + w, maxpos[1] + h)
        ).random_point(), region)


    def find_in_client(self, item_ref):
        screen = grabber.grab(self.screen_bounds)
        _ = np.array(screen)
        screen = np.array(screen.convert("L"))
        template = cv2.imread(item_ref, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= self.client_threshold)
        self.reset_client_threshold()
        if len(list(zip(*loc[::-1]))) < 1:
            debug("CLIENT_SEARCH_ERROR: %s" % item_ref)
            return None

        for pt in zip(*loc[::-1]):
            if config.DEBUG:
                cv2.rectangle(_, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
                cv2.imwrite('debug/client%s%s/screen_%s.png' % (self.row, self.col, item_ref.split("/")[-1].split(".")[0]), _)
            
            return self.translate(Box(
                Pos(*pt),
                Pos(pt[0] + w, pt[1] + h)
            ).random_point())
        

    def translate(self, pos, region=None):
        if region is not None:
            pos.add(region.tl)
        return pos.add(self.screen_bounds.tl)


    def set_client_threshold(self, val):
        if not 0 < val < 1:
            debug("Session - set_client_threshold: Value is not between 0 and 1")
            return self
        self.client_threshold = val
        return self


    def set_region_threshold(self, val):
        if not 0 < val < 1:
            debug("Session - set_region_threshold: Value is not between 0 and 1")
            return self
        self.region_threshold = val
        return self


    def reset_client_threshold(self):
        self.client_threshold = 0.8


    def reset_region_threshold(self):
        self.region_threshold = 0.3


    def reset_login_time(self):
        self._login_time = time.time()

    def get_login_length(self):
        return time.time() - self._login_time


    def set_login_time_max(self, min_time, max_time):
        self._login_time_max = random.randint(min_time, max_time)
    

    def should_log_out(self):
        return self.get_login_length() > self._login_time_max
