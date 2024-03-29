import matplotlib.pyplot as plt
from darkflow.net.build import TFNet
import cv2
import numpy as np
import random
import time

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
        topleft = Pos(
            x=rock["topleft"]["x"],
            y=rock["topleft"]["y"]
        )
        bottomright = Pos(
            x=rock["bottomright"]["x"],
            y=rock["bottomright"]["y"]
        )
        bbox_result.append((
            topleft.x,
            topleft.y,
            (bottomright.x - topleft.x),
            (bottomright.y - topleft.y)
        ))
    return bbox_result


def initialise_tracker():
    # Read in first frame
    img_path = grabber.grab_fullscreen(file_name="stream", save=True)
    imlib.rescale(img_path).save("stream.png")
    # frame = imlib.rescale_obj(grabber.grab_fullscreen())
    # frame = np.array(frame)
    frame = cv2.imread("stream.png")

    # Get bbox using TFNet
    print("> Initial predictions...")
    predictions = TF_NET.return_predict(frame)
    print("> Translations...")
    bboxes = translate_predictions_to_bbox(predictions)

    # Initialise Multi-Tracker
    print("> Setup initialising...")
    tracker = cv2.MultiTracker_create()
    tracker_colours = []
    for bbox in bboxes:
        tracker.add(cv2.TrackerKCF_create(), frame, bbox)
        tracker_colours.append((
            random.randint(1, 255),
            random.randint(1, 255),
            random.randint(1, 255)
        ))
    return tracker, tracker_colours


print("Starting up a tracker...")
tracker, tracker_colours = initialise_tracker()
print("... done.")


print("Starting stream...")
refresh_tracker_timer = time.time()
while True:
    # if time.time() - refresh_tracker_timer > 7:
    #     print("Refreshing tracker...")
    #     refresh_tracker_timer = time.time()
    #     tracker, tracker_colours = initialise_tracker()
    
    # Get next frame
    frame = np.array(imlib.rescale_obj(grabber.grab_fullscreen()))

    # Update tracker
    print("> Updating tracker...")
    success, boxes = tracker.update(frame)
    print("Tracker success: %s || Box Count: %s" % (success, len(boxes)))

    # Draw bounding boxes
    if success:
        for i, box in enumerate(boxes):
            p1 = (int(box[0]), int(box[1]))
            p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
            cv2.rectangle(frame, p1, p2, tracker_colours[i], 2, 1)

    # Show stream
    cv2.imshow('test', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Stream cleanup
cv2.destroyAllWindows()
