import time
import random

import cv2
import numpy as np

# Custom Library
from tools import client_handler as handler
from tools.lib import file_name
from tools.screen_pos import Pos, Box
from tools import config
from debug import debug
from tools.lib import debug as console


class Client:
    def __init__(self, name, client, host):
        # Thread safety
        self._exit_thread = False

        # Instance
        self.name = name
        self.client = client
        self.host = host

        # Thresholds
        self.threshold = .5

        # Timers
        self._login_time = time.time()
        self._login_time_max = 300 * 60

    # UI Events

    def click(self, pos):
        handler.click(self.client, pos.x, pos.y)

    def key(self, key):
        handler.keypress(self.client, self.host, key)

    # UI search

    def find(self, item_ref, region=None, return_box=False):
        screen = handler.screenshot(self.host, region)
        _ = np.array(screen)
        screen = np.array(screen.convert("L"))
        template = cv2.imread(item_ref, 0)
        w, h = template.shape[::-1]

        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        maxpos = cv2.minMaxLoc(res)
        if maxpos[1] < self.threshold:
            maxpos = maxpos[3]
            cv2.rectangle(
                _, maxpos, (maxpos[0] + w, maxpos[1] + h), (25, 0, 255), 1)
            cv2.imwrite('debug/%s/fail_region_%s.png' %
                        (self.name, file_name(item_ref)), _)
            return None

        self.reset_threshold()
        maxpos = cv2.minMaxLoc(res)[3]

        if config.DEBUG:
            cv2.rectangle(
                _, maxpos, (maxpos[0] + w, maxpos[1] + h), (25, 0, 255), 1)
            cv2.imwrite('debug/%s/region_%s.png' %
                        (self.name, file_name(item_ref)), _)

        pnt = Box(
            Pos(*maxpos),
            Pos(maxpos[0] + w, maxpos[1] + h)
        )
        if return_box:
            if region is not None:
                pnt.tl.add(region.tl)
                pnt.br.add(region.tl)
            return pnt
        pnt = pnt.random_point()
        if region is not None:
            pnt.add(region.tl)

        return pnt

    def set_threshold(self, threshold):
        self.threshold = threshold
        return self

    def reset_threshold(self):
        self.threshold = .5

    # Debug

    def info(self, msg):
        debug.info("[%s] - %s" % (self.name, msg))

    def warn(self, msg):
        debug.warn("[%s] - %s" % (self.name, msg))
    
    def log(self, msg):
        console("[%s] - %s" % (self.name, msg))

    # Thread management

    def exit(self):
        self._exit_thread = True

    def should_exit(self):
        return self._exit_thread

    # Timers

    def reset_login_time(self):
        self._login_time = time.time()

    def get_login_length(self):
        return time.time() - self._login_time

    def set_login_time_max(self, min_time, max_time):
        self._login_time_max = random.randint(min_time, max_time)

    def should_log_out(self):
        return self.get_login_length() > self._login_time_max
