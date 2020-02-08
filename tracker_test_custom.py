import matplotlib.pyplot as plt
from darkflow.net.build import TFNet
import cv2
import numpy as np
import random
import time

import sys

import tools.osrs_screen_grab as grabber
from tools import config
import tools.image_lib as imlib
from tools.screen_pos import Pos
from tools import config
from tools.session import Session


# Load in TFNet
TFNET_OPTIONS = {
    # "model": "cfg/yolo-kratos.cfg",
    # "load": -1,
    "pbLoad": "brain_tanner/yolo-kratos.pb",
    "metaLoad": "brain_tanner/yolo-kratos.meta",
    "labels": "./labels.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)


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


def initialise_trackers(session):
    # Read in first frame
    # img_path = grabber.grab(session.screen_bounds, None, file_name="stream", save=True)
    # imlib.rescale(img_path).save("stream.png")
    # frame = cv2.imread("stream.png")
    frame = np.array(imlib.rescale_obj(grabber.grab(session.screen_bounds)))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # cv2.imwrite('debug/test.png', frame)

    # Get bbox using TFNet
    print("> Initial predictions...")
    predictions = TF_NET.return_predict(frame)
    print("> Translations...")
    bboxes = translate_predictions_to_bbox(predictions)

    # Initialise Multi-Tracker
    print("> Setup initialising...")
    trackers = []
    tracker_colours = []
    for bbox in bboxes:
        tracker = cv2.TrackerKCF_create()
        tracker.init(frame, bbox)
        trackers.append(tracker)
        tracker_colours.append((random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)))
        
    return trackers, tracker_colours



session = Session(0, 0)

print("Starting up a tracker...")
trackers, tracker_colours = initialise_trackers(session)
print("... done.")
print("Tracker Count: %s" % len(trackers))


print("Starting stream...")
refresh_tracker_timer = time.time()
while True:
    if time.time() - refresh_tracker_timer > 2:
        print("Refreshing tracker...")
        refresh_tracker_timer = time.time()
        trackers, tracker_colours = initialise_trackers(session)
    
    # Get next frame
    frame = np.array(imlib.rescale_obj(grabber.grab(session.screen_bounds)))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Update tracker
    # print("> Updating trackers...")
    for i, tracker in enumerate(trackers):
        success, bbox = tracker.update(frame)
        # Draw bounding boxes
        if success:
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, tracker_colours[i], 2, 1)

    # Show stream
    cv2.imshow('test', frame)
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

# Stream cleanup
cv2.destroyAllWindows()
