#!/usr/bin/env python
import cv2

class Annotated_object:

    def __init__(self, poly, classname):
        self.poly = poly
        self.classname = classname
        x, y, w, h = cv2.boundingRect(self.poly)
        self.bbox = [x,y, x+w, y+h]

    def __str__(self):
        return "{0} at {1}".format(self.classname, self.bbox)
