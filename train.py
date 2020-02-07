import matplotlib.pyplot as plt
import numpy as np

from darkflow.net.build import TFNet
import cv2

options = {
    "model": "cfg/yolo-kratos.cfg",
    "load": "bin/yolo.weights",
    "batch": 2,
    "epoch": 1000,
    "gpu": 1.0,
    "train": True,
    # "load": -1,
    # "labels": "./classes.txt",
    "annotation": "./RAW_DATA/annotations/",
    "dataset": "./RAW_DATA/"
}

print("--------------------- STARTING BOOTUP ---------------------")
tfnet = TFNet(options)

print("--------------------- STARTING TRAINING ---------------------")
tfnet.train()