#!/usr/bin/env python
from lib import mask
from lib import annotated_object
import numpy as np
import cv2
import os
import pickle
import argparse

""" annotate.py                                                      2017-03-13
written by Matthias Kardel <mkardel@gmail.com>

Features missing:
    - save annotations in pascal voc format

Features completed:
    - create masks
    - create annotations

Usage:

    Start via python annotate.py --source=VIDEO_SOURCE

    1. Click polygons with left mouse button, delete last point with right.
    2. Save polygon by pressing n.
    3. Delete last polygon by pressing d.
    4. Advance to next frame by pressing space.

"""

# Globally used variables
points = False
coords = False
truncated = False

cachefile = '.a_cache'

def clicker_event(event, x, y, flags, param):
    global points
    # save point to polygon
    if event == cv2.EVENT_LBUTTONDOWN:
        if isinstance(points, bool): #first run
            points = np.array([ [x,y] ])
        else:
            points = np.append( points, [[x,y]], axis=0) 
    elif event == cv2.EVENT_RBUTTONDOWN:
        if not isinstance(points, bool) and len(points) > 0:
            points = np.delete(points,len(points)-1,0)

# Draw points from the global points array.
def draw_points(image, points):
    col = (0, 233, 0)
    if not isinstance(points, bool):
        if len(points) == 1: # Draw only one point
            p = tuple(points[0][0])
            cv2.line(image, p, p, col, 2)
            print("drawing points")

        for i in xrange(len(points)-1):
            point = points[i]
            next_point = points[i+1]
            cv2.line(image, tuple(point[0]), tuple(next_point[0]), col, 2)
    return image

# Create annotations for a video file.
def annotate_video(source_video):
    global points
    m = None
    annotations = []
    is_running = True

    vid = cv2.VideoCapture(source_video)

    while(vid.isOpened()):
        if is_running:
            ret, frame = vid.read()
        else:
            break
        
        polys = []

        if ret:
            while is_running:
                image = frame.copy()

                # Create a mask, try to load mask or create new mask
                if m is None:
                    m = mask.Mask(source_video, image)
                image = cv2.bitwise_and(image, image, mask=m.mask)
                cv2.setMouseCallback('Annotate', clicker_event)
    
                cv2.imshow('Annotate', image)
                
                key = cv2.waitKey(20) & 0xFF 
                
                # Quit on q
                if key == ord('q'):
                    is_running = False

                # Add object with n
                if key == ord('n'):
                    a = annotated_object.Annotated_object(points, 'test')
                    annotations.append(a)
                    print(points)
                    points = False

                # Delete latest annotated object with d
                if key == ord('d'):
                    if len(annotations) > 0:
                        annotations.pop()

                # Next image 
                if key == 32:
                    # Add annotation for al
                    for annot in annotations:
                        print("Adding annotations: {}".format(annot))
                    break
        else:
            break
    
    print("Saving all annotations")

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
        annotations = annotate_video(args.source_video)
        for annot in annotations:
            annot.save()
    else:
        error = "Path not found at {0}".format(args.source_video)
        raise IOError(error)
