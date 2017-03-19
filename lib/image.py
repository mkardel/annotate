#!/usr/bin/env python
import cv2

# An image holds a list of annotated objects
class Image:

    def __init__(self, annotated_objects=None):
        if annotated_objects is None:
            self.annotated_objects = []
        else:
            self.annotated_objects = annotated_objects

    def __str__(self):
        print("{} objects:".format(len(self.annotated_objects)))
        for o in self.annotation_objects:
            print(o)
