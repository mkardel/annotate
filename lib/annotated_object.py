#!/usr/bin/env python
import cv2


class AnnotatedObject(object):
    def __init__(self, poly, classname, truncated, difficult=False):
        self.poly = poly
        self.classname = classname
        x, y, w, h = cv2.boundingRect(self.poly)
        self.bbox = [x, y, x+w, y+h]
        self.truncated = truncated
        self.difficult = difficult

    def __str__(self):
        return "{0} at {1}".format(self.classname, self.bbox)
