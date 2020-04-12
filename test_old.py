import matplotlib.pyplot as plt
import numpy as np
import cv2
import time

from darkflow.net.build import TFNet

# Custom Library
import tools.image_lib as imlib


# Image Constants
WIDTH = 1494
HEIGHT = 840


# Load TFNet
TFNET_OPTIONS = {
    "model": "cfg/yolo-kratos.cfg",
    "gpu": 1.0,
    "load": -1,
    "labels": "./classes.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)
TF_NET.load_from_ckpt()


# Timing
CURRENT_TIME = time.time()
def log_time(log_str):
    global CURRENT_TIME
    print("%s: %s" % (log_str, time.time() - CURRENT_TIME))
    CURRENT_TIME = time.time()


def boxing(original_image, predictions):
    new_image = np.copy(original_image)

    for result in predictions:
        top_x = result['topleft']['x']
        top_y = result['topleft']['y']

        bottom_x = result['bottomright']['x']
        bottom_y = result['bottomright']['y']

        confidence = result['confidence']
        label = result['label'] + " " + str(round(confidence, 3))

        if confidence > 0.3:
            new_image = cv2.rectangle(new_image, (top_x, top_y), (bottom_x, bottom_y), (255, 0, 0), 3)
            new_image = cv2.putText(new_image, label, (top_x, top_y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, (0, 230, 0), 1, cv2.LINE_AA)

    return new_image



def main():
    print("Starting test")

    # Image Processing
    img_path = "./RAW_TEST_DATA/test2.png"
    imlib.rescale(img_path, WIDTH, HEIGHT).save('current.png')
    current_img = cv2.imread('current.png')

    # TFNet Call
    log_time("Start predictions")
    predictions = TF_NET.return_predict(current_img)
    log_time("End predictions")

    # Analysing
    fig, ax = plt.subplots(figsize = (20, 10))
    ax.imshow(boxing(current_img, predictions))
    plt.show()



if __name__ == "__main__":
    main()
