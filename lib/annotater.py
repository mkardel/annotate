#!/usr/bin/env python

from lib.exporter import pascal_voc
import numpy as np
import cv2
import os
import pickle

from .importer import PascalVOCImporter, VideoImporter

from .annotated_object import AnnotatedObject
from . import mask
from . import image
from .image_input import ImageInput

dataset_type_importer = {
    'video': VideoImporter,
    'pascal_voc': PascalVOCImporter
}


class Annotater(object):
    def __init__(self, input_path, dataset_type='pascal_voc', use_mask=False):
        self.input_path = input_path
        self.dataset_type_str = dataset_type
        importer = dataset_type_importer.get(self.dataset_type_str)
        importer_instance = importer(input_path)
        self.dataset = importer_instance.create_dataset()

        # Globally used variables
        self.points = False
        self.truncated = False

        self.cachefile = '.a_cache'
        
        # So far, only one classname is possible, feel free to enable more
        self.classname = 'aeroplane'
        self.use_mask = use_mask
        self.annotate_dataset()

    def clicker_event(self, event, x, y, flags, param):
        # save point to polygon
        if event == cv2.EVENT_LBUTTONDOWN:
            if isinstance(self.points, bool): #first run
                self.points = np.array([ [x,y] ])
            else:
                self.points = np.append( self.points, [[x,y]], axis=0) 
        elif event == cv2.EVENT_RBUTTONDOWN:
            if not isinstance(self.points, bool) and len(self.points) > 0:
                self.points = np.delete(self.points, len(self.points)-1,0)

    def draw_points(self, im):
        col = (0, 233, 0)
        if not isinstance(self.points, bool):
            if len(self.points) == 1: # Draw only one point
                p = tuple(self.points[0])
                cv2.line(im, p, p, col, 2)

            for i in range(len(self.points)-1):
                point = self.points[i]
                next_point = self.points[i+1]
                cv2.line(im, tuple(point), tuple(next_point), col, 2)
        return im

    def draw_poly(self, im, pts, col=(255,255,255)):
        cv2.fillConvexPoly(im, pts, col)
        return im

    def draw_annotation(self, im, name, pts, col=(255,255,255)):
        for pt1, pt2 in zip(pts[:-1], pts[1:]):
            cv2.line(im, tuple(pt1), tuple(pt2), col)
        cv2.line(im, tuple(pts[-1]), tuple(pts[0]), col)
        cv2.putText(img=im,
                    text=name,
                    org=tuple(pts[0]),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=0.5,
                    color=col)
        return im

    def annotate_dataset(self):
        m = None
        is_running = True

        if os.path.isfile(self.cachefile):
            self.dataset = pickle.load(open(self.cachefile, 'rb'))

        while self.dataset is not None:
            annotations = self.dataset.get_annotations()

            if is_running:
                _, frame = self.dataset.get_image()
            else:
                break

            polys = []

            w = cv2.namedWindow('Annotate')
            cv2.setMouseCallback('Annotate', self.clicker_event)

            while is_running:
                im = frame.copy()

                # Create a mask, try to load mask or create new mask
                if self.use_mask:
                    if m is None:
                        m = mask.Mask(source_video, im)
                    im = cv2.bitwise_and(im, im, mask=m.mask)

                # Draw the currently added points
                if (not isinstance(self.points, bool) and
                        len(self.points) > 0):
                    im = self.draw_points(im)

                # Draw the up until now added polygons
                for p in annotations:
                    # im = self.draw_poly(im, p.poly)
                    im = self.draw_annotation(im, p.classname, p.poly)

                cv2.imshow('Annotate', im)

                key = cv2.waitKey(20) & 0xFF

                # Fast forward, skip 100 frames in either direction
                if key == ord(']'):
                    self.dataset.inc_index(100)
                    # current_index = min(current_index + 100, max_index - 1)
                elif key == ord('['):
                    self.dataset.dec_index(100)
                    # current_index = max(current_index - 100, 0)

                # Quit on q
                if key == ord('q'):
                    is_running = False

                # Add object with n
                if key == ord('n'):
                    if not isinstance(self.points, bool) and len(self.points) > 3:
                        a = AnnotatedObject(self.points,
                                            self.classname,
                                            self.truncated)
                        annotations.append(a)
                        self.points = False

                # Delete latest annotated object with d
                if key == ord('d'):
                    if len(annotations) > 0:
                        annotations.pop()

                # Toggle object truncation
                if key == ord('t'):
                    self.truncated = not self.truncated
                    print("Truncated is set to: {}".format(self.truncated))

                # Next im and save
                if key == 32:
                    self.dataset.set_annotations(annotations)
                    annotations = []
                    pickle.dump(self.dataset, open(self.cachefile, 'wb'))

                if key == 83 or key == 32 or key == ord(']'):  # right or space
                    self.dataset.inc_index()
                    break

                elif key == 81 or key == ord('['):  # left
                    self.dataset.dec_index()
                    break
