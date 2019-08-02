import cv2

from ..dataset import VideoDataset


class VideoImporter(object):
    def __init__(self, path):
        self.path = path
        self.annotations = []
        self.images = []

    def validate(self):
        try:
            cap = cv2.VideoCapture(self.path)
            cap.release()
        except Exception as e:
            pass

    def create_dataset(self):
        cap = cv2.VideoCapture(self.path)
        while cap.isOpened():
            max_annots = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            while max_annots > 0:
                annotation = []
                self.annotations.append(annotation)
                max_annots -= 1
            break
        cap.release()
        return VideoDataset(self.path,
                            None,
                            None,
                            self.annotations)
