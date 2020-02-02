import cv2
import numpy as np
from matplotlib import pyplot as plt

from tools.screen_pos import Pos


inv = cv2.imread("bot_ref_imgs/inv_dropmode.png")
inv_gray = cv2.cvtColor(inv, cv2.COLOR_BGR2GRAY)
copper_template = cv2.imread("bot_ref_imgs/copper.png", 0)

w, h = copper_template.shape[::-1]

res= cv2.matchTemplate(inv_gray, copper_template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8
loc = np.where(res >= threshold)


drawn = []

for pt in zip(*loc[::-1]):

    check = [pos for pos in drawn if (-5 <= pos.x - pt[0] <= 5) and (-5 <= pos.y - pt[1] <= 5)]
    if len(check) > 0:
        continue

    drawn.append(Pos(pt[0], pt[1]))
    cv2.rectangle(inv, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)

print("drawn: %s" % len(drawn))
cv2.imwrite('debug/current_inv.png', inv)