#!/usr/bin/env python
from lib import annotater
import argparse
import os

""" annotate.py                                                      2017-03-13
written by Matthias Kardel <mkardel@gmail.com>

Usage:

    Start via python annotate.py --source=VIDEO_SOURCE

    1. Click polygons with left mouse button, delete last point with right.
    2. Save polygon by pressing n.
    3. Delete last polygon by pressing d.
    4. Advance to next frame by pressing space.
"""

def parse_args():
    parser = argparse.ArgumentParser(description='Object Annotation script for PASCAL_VOC')
    parser.add_argument('--source', dest='source_video',
                        help='Define the location of a source video',
                        default=None, type=str)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    
    args = parse_args()
    if os.path.isfile(args.source_video):
        annotater.Annotater(args.source_video)
    else:
        error = "Path not found at {0}".format(args.source_video)
        raise IOError(error)
