#!/usr/bin/env python
from os.path import exists, join
from os import listdir, makedirs
import cv2
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment
import xml.etree.ElementTree as ElementTree
import codecs 

"""
Create the necessary dirs for a Pascal VOC dataset and store images,
masks and annotations accordingly
"""

class PascalVoc:

    def __init__(self, path='VOC2007'):

        self.path = path
        self._create_dirs()

    def _create_dirs(self):

        # Setup directories first
        if not exists(self.path):
            makedirs(self.path)
        
        pascal_dirs = ['Annotations', 'ImageSets', 'ImageSets/Main',
                'JPEGImages', 'SourceImages', 'SourceMasks']

        for d in pascal_dirs:
            if not exists(join(self.path, d)):
                makedirs(join(self.path, d))

    # Annotations are sorted numerically, therefore the next annotation
    # should be numbered total + 1
    def _get_latest_image_number(self):
        annot_path = join(self.path, 'Annotations')
        annots = listdir(annot_path)
        return len(annots) + 1

    def save(self, image, annotations):
        number = self._get_latest_image_number()
        self._save_image(number, image)
        self._save_annotations(number, annotations, image)

    def _save_image(self, number, image):
        im_name = "{0:06d}.jpg".format(number)
        im_path = join(self.path, 'JPEGImages', im_name)
        cv2.imwrite(im_path, image)

    def _save_annotations(self, number, annotations, image):
        annot_name = "{0:06d}.xml".format(number)
        annot_path = join(self.path, 'Annotations', annot_name)

        top = Element('annotation')
        folder = SubElement(top, 'folder')
        folder.text = 'VOC2007'

        filename = SubElement(top, 'filename')
        #use 6 digits for the number (zero padding)
        filename.text = "{0:06d}.jpg".format(number)
        source = SubElement(top, 'source')

        database = SubElement(source, 'database')
        database.text = 'The VOC2007 Database'
        annotation = SubElement(source, 'annotation')
        annotation.text = 'PASCAL VOC20007'
        im = SubElement(source, 'image')
        im.text = 'non flickr'

        owner = SubElement(top, 'owner')
        name = SubElement(owner, 'name')
        name.text = 'Anonymous'

        size = SubElement(top, 'size')  
        width_ = SubElement(size, 'width')
        width_.text = str( image.shape[1] )
        height_ = SubElement(size, 'height')
        height_.text = str( image.shape[0] )
        depth = SubElement(size, 'depth')
        depth.text = str( image.shape[2] )
        
        segmented = SubElement(top, 'segmented')
        segmented.text = '0'

        for _o in annotations:

            rect = _o.bbox

            object_ = SubElement(top, 'object')
            o_name = SubElement(object_, 'name')
            o_name.text = _o.classname
                            
            o_pose = SubElement(object_, 'pose')
            o_pose.text = 'Unspecified'

            trunc = _o.truncated
            o_truncated = SubElement(object_, 'truncated')
            if trunc:
                o_truncated.text = '1'
            else:
                o_truncated.text = '0'

            # Set difficult always to 0
            o_difficult = SubElement(object_, 'difficult')
            o_difficult.text = '0'

            bndbox = SubElement(object_, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(max(rect[0] + 1, 0))
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(max(rect[1] + 1, 0))
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(min(rect[2] + 1, image.shape[1]))
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(min(rect[3] + 1, image.shape[0]))

            """
            # Only save polygon information, if they are there.
            # Normal pascal voc datasets save no polygonal
            # information within the xml file.
            if _o._poly is not None and not isinstance(_o._poly, bool) \
                and not stripped and len(_o._poly) > 0:

                # save points from polygon
                poly = SubElement(object_, 'polygon')

                for point in _o._poly:
                    x = int(point[0][0])
                    y = int(point[0][1])
                    poly_point = SubElement( poly, 'point' )
                    poly_point_x = SubElement( poly_point, 'x')
                    poly_point_x.text = str(min(x + 1, _shape[1]))
                    poly_point_y = SubElement( poly_point, 'y')
                    poly_point_y.text = str(min(y + 1, _shape[0]))
            """

        # Save to xml
        # This looks rather idiotic, but the parseing to string and
        # then parsing to XML was needed to keep the absolutely correct
        # amounts of tabs and spaces in the XML file. Otherwise the matlab
        # scripts, provided by the PASCAL VOC team for evaluation, will not
        # work properly.
        top_string = ElementTree.tostring(top)#, encoding='utf-8')
        dom = minidom.parseString(top_string)

        file_handle = codecs.open(annot_path,"wb","UTF-8")
        file_handle.write(dom.toprettyxml(indent='\t')[23:])
        #file_handle.write(dom.toprettyxml(indent='\t'))#,encoding='UTF-8'))
        file_handle.close()
