#!/usr/bin/env python
from lib import annotater
import argparse
import os

""" annotate.py                                                      2017-03-13
written by Matthias Kardel <mkardel@gmail.com>

Usage:

    Start via python annotate.py --source=VIDEO_PATH --dataset-type=VIDEO

    1. Click polygons with left mouse button, delete last point with right.
    2. Save polygon by pressing n.
    3. Delete last polygon by pressing d.
    4. Advance to next frame by pressing space.
"""


def parse_args():
    parser = argparse.ArgumentParser(description='Object Annotation script for PASCAL_VOC')
    parser.add_argument('--source',
                        dest='source_video',
                        help='Define the location of a source video',
                        default=None,
                        type=str)
    parser.add_argument('--dataset-type',
                        dest='dataset_type',
                        help='Define the name of the dataset, i.e. pascal-voc',
                        default='pascal_voc',
                        type=str)
    parser.add_argument('--mask', action='store_true', dest='use_mask',
                        help='Usage of masks')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    
    args = parse_args()
    try:
        annotater.Annotater(args.source_video, args.dataset_type, args.use_mask)
    except IOError as e:
        error = "Path not found at {0}".format(args.source_video)
        raise e
