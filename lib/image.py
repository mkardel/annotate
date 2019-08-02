#!/usr/bin/env python
import cv2


class Image(object):
    """Image class holds a list of annotations"""
    def __init__(self, annotated_objects=None):
        if annotated_objects is None:
            self.annotated_objects = []
        else:
            self.annotated_objects = annotated_objects

    def __str__(self):
        print("{} objects:".format(len(self.annotated_objects)))
        for o in self.annotation_objects:
            print(o)
