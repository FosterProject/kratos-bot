import cv2
import numpy as np
from PIL import ImageGrab

from tools import config

while True:
    frame = ImageGrab.grab(bbox=(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)).convert('RGB')
    frame = np.array(frame)

    cv2.imshow('test', frame)

    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
