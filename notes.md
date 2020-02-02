# OSRS Bot - Darkflow Edition

## Installation

1. Create the virtual env: `conda create -n Kratos python=3.7.6 anaconda`
2. Install tensorflow: `conda install -c anaconda tensorflow-gpu=1.15.0`
3. Install opencv: `pip install opencv-python`
    - `pip install Pillow`
    - `pip install pyautogui`
4. Cloned darknet into root folder: `git clone https://github.com/thtrieu/darkflow.git`
5. Set up darkflow: `cd darkflow` -> `python setup.py build_ext --inplace`

## Preparation for Training

- Copy a yolo config file from the *cfg* directory (yolo.cfg / tiny-yolo.cfg).
- Change the filters value in last [convolutional] section to (($num_classes + 5) * 5).
- Change the no of classes in the [region] to the number of classes.
- Create a *classes.txt* with a class name per line.

- Transfer Learning the new model: `python flow --train --model .\cfg\yolo-kratos.cfg --load .\bin\yolo.weights --gpu 1.0`

- Training: `python flow --model .\cfg\yolo-kratos.cfg --labels .\classes.txt --train --trainer george --dataset .\RAW_DATA\ --annotation .\RAW_DATA\annotations\ --gpu 1.0`
    - To restart from last checkpoint, add `--load -1` to the previous command.
- Test: `python flow --model .\cfg\yolo-kratos.cfg --imgdir .\RAW_TEST_DATA\ --labels .\classes.txt --load -1 --gpu 1.0`


## Training Notes

- I had to run with a batch of 2
- I had to resize the cfg down to 416x416.
- Make sure that your training data images are square and a smallish resolution < 500. (I used 480x480)
- 1000 epochs was good enough for a base copper rock.


## Resources

- [Custom Object Detection using yolo and Darkflow](https://medium.com/coinmonks/detecting-custom-objects-in-images-video-using-yolo-with-darkflow-1ff119fa002f)
