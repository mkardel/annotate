#!/usr/bin/env python

from os.path import exists, join, splitext
from os import listdir, makedirs
import xml.etree.ElementTree as ElementTree

import numpy

from ..dataset import Dataset
from ..image_input import InputImages
from ..annotated_object import AnnotatedObject


class AnnotateException(Exception):
    pass


class DatasetIntegrityError(AnnotateException):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


class PascalVOCImporter(object):
    """Import a dataset, that is in pascal voc format"""
    IMAGE_DIR = 'JPEGImages'
    ANNOTATION_DIR = 'Annotations'

    PASCAL_DATASET_DIRS = [ANNOTATION_DIR,
                           'ImageSets',
                           'ImageSets/Main',
                           IMAGE_DIR]

    def __init__(self, path='VOC2007'):
        self.images = None
        self.annotations = None
        self.path = path
        self.validate_dataset()
        self.load_data()

    def validate_dataset(self):
        for d in self.PASCAL_DATASET_DIRS:
            full_path = join(self.path, d)
            if not exists(full_path):
                raise DatasetIntegrityError('{} does not exist in filesystem'.format(full_path),
                                            IOError)

    @staticmethod
    def pascal_voc_annotation_importer(annotation_dir):
        annotations = []
        annotation_files = listdir(annotation_dir)
        annotation_files.sort()

        def extract_annotated_object(annotation):
            name = annotation.find('name').text
            truncated = bool(annotation.find('truncated').text)
            difficult = bool(annotation.find('difficult').text)
            bndbox = annotation.find('bndbox')
            xmin = int(bndbox.find('xmin').text)
            xmax = int(bndbox.find('xmax').text)
            ymin = int(bndbox.find('ymin').text)
            ymax = int(bndbox.find('ymax').text)
            poly = numpy.asarray([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)])
            return AnnotatedObject(poly, name, truncated, difficult)

        for f in annotation_files:
            annotations_per_image = []
            annotation_file = join(annotation_dir, f)
            tree = ElementTree.parse(annotation_file)
            root = tree.getroot()
            for _object in root.iter('object'):
                annotation = extract_annotated_object(_object)
                annotations_per_image.append(annotation)
            annotations.append(annotations_per_image)
        return annotations

    def load_data(self):
        image_dir = join(self.path, self.IMAGE_DIR)
        self.images = InputImages(image_dir)
        annotation_dir = join(self.path, self.ANNOTATION_DIR)
        self.annotations = PascalVOCImporter.pascal_voc_annotation_importer(annotation_dir)

    def create_dataset(self):
        return Dataset(join(self.path, self.IMAGE_DIR),
                       join(self.path, self.ANNOTATION_DIR),
                       self.images,
                       self.annotations)
