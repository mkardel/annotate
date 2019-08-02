from os import listdir
from os.path import isdir
from os.path import isfile
from os.path import join

import cv2


class ImageInput(object):
    """
    Represent input images, either as video stream or directory with images
    """

    def __init__(self, source=None):

        self.index = 0
        if isfile(source):
            self = _InputVideo(source)
        elif isdir(source):
            self = InputImages(source)
        else:
            self = None

    def set_index(self):
        pass

    def get_image(self):
        pass

    def get_index(self):
        self.index


class InputImages(object):

    def __init__(self, source):
        self.index = 0
        self.images = [join(source, f) for f in listdir(source)]
        self.images.sort()
        self.max_index = len(self.images)

    def _get_image(self, idx=0):
        im = cv2.imread(self.images[idx])
        return im

    def set_index(self, idx):
        if 0 <= idx < (self.max_index - 1):
            self.index = idx
        elif idx < 0:
            self.index = 0
        elif idx > self.max_index:
            self.index = self.max_index - 1

    def dec_index(self, idx=1):
        self.set_index(self.index - idx)

    def inc_index(self, idx=1):
        self.set_index(self.index + idx)

    def next_image(self):
        self.inc_index()
        im = self.get_image()
        return im

    def prev_image(self):
        self.dec_index()
        im = self.get_image()
        return im

    def get_image(self, idx=None):
        if idx is not None:
            self.set_index(idx)
        im = self._get_image(self.index)
        return im


class _InputVideo(object):

    def __init__(self, source):
        self.vid = cv2.VideoCapture(source)
        self.max_index = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

    def set_index(self):
        pass

    def next_image(self):
        return None

    def prev_image(self):
        return None

    def get_image(self, idx=None):
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, idx)
        return None
