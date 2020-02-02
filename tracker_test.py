import matplotlib.pyplot as plt
from darkflow.net.build import TFNet
import cv2
import numpy as np
import random

import tools.osrs_screen_grab as grabber
from tools import config
import tools.image_lib as imlib
from tools.screen_pos import Pos
from tools import config


# Window Constants (Used for an artificial (0,0) coord when translating click region back to screen)
TRANSLATION_DIST = ((config.SCREEN_HEIGHT / 2) - (config.SCREEN_HEIGHT / 15))
TRANSLATION_TOPLEFT = Pos((config.SCREEN_WIDTH / 2) - TRANSLATION_DIST, (config.SCREEN_HEIGHT / 2) - TRANSLATION_DIST)


# Load in TFNet
TFNET_OPTIONS = {
    "model": "cfg/yolo-kratos.cfg",
    "gpu": 1.0,
    "load": -1,
    "labels": "./classes.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)
TF_NET.load_from_ckpt()


def translate_predictions_to_bbox(rocks):
    bbox_result = []
    rocks = [rock for rock in rocks if rock["confidence"] > 0.5]
    for rock in rocks:
        topleft = imlib.upscale(Pos(
            x=rock["topleft"]["x"],
            y=rock["topleft"]["y"]
        ))
        bottomright = imlib.upscale(Pos(
            x=rock["bottomright"]["x"],
            y=rock["bottomright"]["y"]
        ))
        bbox_result.append((
            TRANSLATION_TOPLEFT.x + topleft.x,
            TRANSLATION_TOPLEFT.y + topleft.y,
            (bottomright.x - topleft.x),
            (bottomright.y - topleft.y)
        ))
    return bbox_result


# Read in first frame
frame = grabber.grab_fullscreen("stream", True)
imlib.rescale(frame).save("stream_initial.png")
stream_initial = cv2.imread("stream_initial.png")

# Get bbox using TFNet
print("Initial predictions...")
predictions = TF_NET.return_predict(stream_initial)
print("Translations...")
bboxes = translate_predictions_to_bbox(predictions)

# Initialise Multi-Tracker
print("Tracker initialising...")
frame_img = cv2.imread(frame)
tracker = cv2.MultiTracker_create()
tracker_colours = []
for bbox in bboxes:
    tracker.add(cv2.TrackerBoosting_create(), frame_img, bbox)
    tracker_colours.append((
        random.randint(1, 255),
        random.randint(1, 255),
        random.randint(1, 255)
    ))

print("Starting stream...")
while True:
    # Get next frame
    frame = np.array(grabber.grab_fullscreen())

    # Update tracker
    print("Updating tracker...")
    success, boxes = tracker.update(frame)

    # Draw bounding boxes
    for i, box in enumerate(bboxes):
        p1 = (int(box[0]), int(box[1]))
        p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
        cv2.rectangle(frame, p1, p2, tracker_colours[i], 2, 1)

    # Show stream
    cv2.imshow('test', frame)
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

# Stream cleanup
cv2.destroyAllWindows()
