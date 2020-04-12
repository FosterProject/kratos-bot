from tools import client_handler as handler

class Client:
    def __init__(self, client, host):
        # Thread safety
        self._exit_thread = False

        # Instance
        self.client = client
        self.host = host


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

        if config.DEBUG:
            cv2.rectangle(_, maxpos, (maxpos[0] + w, maxpos[1] + h), (25, 0, 255), 1)
            cv2.imwrite('debug/client%s%s/region_%s.png' % (self.row, self.col, file_name(item_ref)), _)

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
        maxpos = cv2.minMaxLoc(res)
        if maxpos[1] < self.client_threshold:
            cv2.imwrite('debug/client%s%s/fail_client_%s.png' % (self.row, self.col, file_name(item_ref)), _)
            debug("CLIENT_SEARCH_ERROR: %s" % item_ref)
            return None

        self.reset_client_threshold()
        maxpos = cv2.minMaxLoc(res)[3]

        if config.DEBUG:
            cv2.rectangle(_, maxpos, (maxpos[0] + w, maxpos[1] + h), (25, 0, 255), 1)
            cv2.imwrite('debug/client%s%s/client_%s.png' % (self.row, self.col, file_name(item_ref)), _)
        
        return self.translate(Box(
            Pos(*maxpos),
            Pos(maxpos[0] + w, maxpos[1] + h)
        ).random_point())


    # Thread management
    def exit(self):
        self._exit_thread = True

    # Thread management
    def should_exit(self):
        return self._exit_thread
    