import cv2


class Dataset(object):
    """Dataset stores images and annotation data"""
    def __init__(self,
                 image_dir,
                 annotation_dir,
                 images,
                 annotations,
                 max_index=None):
        self.image_dir = image_dir
        self.annotation_dir = annotation_dir
        self.images = images
        self.annotations = annotations
        self.current_index = 0
        self.max_index = max_index if max_index is not None else len(annotations) - 1

    def _get_valid_index(self, idx=None):
        return idx if idx is not None else self.current_index

    def get_image(self, idx=None):
        image = self.images.get_image(self._get_valid_index(idx))
        return image

    def get_annotations(self, idx=None):
        annotation = self.annotations[self._get_valid_index(idx)]
        return annotation

    def get_data(self, idx=None):
        image = self.get_image(idx)
        annotation = self.get_annotations(idx)
        return image, annotation

    def get_index(self):
        return self.current_index

    def set_index(self, idx):
        if idx < self.current_index:
            self.current_index = max(0, idx)
        else:
            self.current_index = min(idx, self.max_index)

    def dec_index(self, idx=1):
        self.set_index(self.current_index - idx)

    def inc_index(self, idx=1):
        self.set_index(self.current_index + idx)

    def set_annotations(self, annotation, idx=None):
        valid_index = self._get_valid_index(idx)
        self.annotations[valid_index] = annotation


class VideoDataset(Dataset):
    def get_image(self, idx=None):
        valid_index = self._get_valid_index(idx)
        cap = cv2.VideoCapture(self.image_dir)
        cap.set(cv2.CAP_PROP_POS_FRAMES, valid_index)
        frame = cap.read()
        cap.release()
        return frame