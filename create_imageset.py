#!/usr/bin/env python
import numpy as np
import os
import random

""" create_imageset.py
Create .txt files containing the names of the imageset for training, validation
and testing for the pascal_voc benchmark.

"""
DATASET_PATH = 'VOC2007'

test = []
train = []
val = []
trainval = []

#test_probality = 0.2
#train_probablity = 0.5

test_probability = 0
train_probability = 1

def save_imagesets(imageset_path):
    with open(os.path.join(imageset_path, "test.txt"), "w") as test_file:
        test_file.write('\n'.join(i for i in test))
    with open(os.path.join(imageset_path, "train.txt"), "w") as train_file:
        train_file.write('\n'.join(i for i in train))
    with open(os.path.join(imageset_path, "val.txt"), "w") as val_file:
        val_file.write('\n'.join(i for i in val))
    with open(os.path.join(imageset_path, "trainval.txt"), "w") as trainval_f:
        trainval_f.write('\n'.join(i for i in trainval))

if __name__ == '__main__':

    # get all files that have an existing annotation
    annotation_path = os.path.join(DATASET_PATH, 'Annotations')
    imageset_path = os.path.join(DATASET_PATH, 'ImageSets', 'Main')

    files = [f for f in os.listdir(annotation_path)]
    files.sort()

    for f in files:
        # strip extenstion
        short_name = os.path.splitext(f)[0]
        # decide whether its testing (p=0.5) or trainval(p=0.5)
        if random.random() < test_probability :
            test.append(short_name)
        else:
            trainval.append(short_name)
            # train (p=0.5) or val (p=0.5)
            if random.random() < train_probability:
                train.append(short_name)
            else:
                val.append(short_name)
    print("ImageSets saved")
    save_imagesets(imageset_path)
