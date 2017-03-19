#!/usr/bin/env python
from . import mask
from . import annotated_object
from . import image
from . import pascal_voc
import numpy as np
import cv2
import os
import pickle

class Annotater:

    def __init__(self, video_path):

        # Globally used variables
        self.points = False
        self.truncated = False

        self.cachefile = '.a_cache'
        
        # So far, only one classname is possible, feel free to enable more
        self.classname = 'aeroplane'

        self.annotate_video(video_path)

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

    # Draw points from the global points array.
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


    # Create annotations for a video file.
    def annotate_video(self, source_video):
        m = None
        is_running = True

        vid = cv2.VideoCapture(source_video)

        current_index = 0
        max_index = vid.get(cv2.CAP_PROP_FRAME_COUNT)

        # Setup the im objects 
        if(os.path.isfile(self.cachefile)):
            all_images = pickle.load(open(self.cachefile, 'rb'))
        else:
            all_images = []
            for i in range(int(max_index)):
                all_images.append(image.Image())

        while(vid.isOpened()):
            annotations = all_images[current_index].annotated_objects
            vid.set(cv2.CAP_PROP_POS_FRAMES, current_index) 

            if is_running:
                ret, frame = vid.read()
            else:
                break
            
            polys = []

            w = cv2.namedWindow('Annotate')
            cv2.setMouseCallback('Annotate', self.clicker_event)

            if ret:
                while is_running:
                    im = frame.copy()

                    # Create a mask, try to load mask or create new mask
                    if m is None:
                        m = mask.Mask(source_video, im)
                    im = cv2.bitwise_and(im, im, mask=m.mask)
                    
                    # Draw the currently added points
                    if(not isinstance(self.points, bool) and 
                            len(self.points) > 0):
                        im = self.draw_points(im)

                    # Draw the up until now added polygons
                    for p in annotations:
                        im = self.draw_poly(im, p.poly)
        
                    cv2.imshow('Annotate', im)
                    
                    key = cv2.waitKey(20) & 0xFF 

                  
                    # Fast forward, skip 100 frames in either direction
                    if key == ord(']'):
                        current_index = min(current_index + 100, max_index - 1)
                    elif key == ord('['):
                        current_index = max(current_index - 100, 0)

                    # Quit on q
                    if key == ord('q'):
                        is_running = False

                    # Add object with n
                    if key == ord('n'):
                        if(not isinstance(self.points, bool) and 
                                len(self.points > 3)):                            
                            a = annotated_object.Annotated_object(self.points,
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
                        all_images[current_index].annotated_objects = annotations
                        annotations = []
                        pickle.dump(all_images, open(self.cachefile, 'wb'))
                        # Add annotation for al
                        #for annot in annotations:
                        #    print("Adding annotations: {}".format(annot))

                    if key == 83 or key == 32 or key == ord(']'): #right or space
                        current_index = min(current_index + 1, max_index-1)
                        break
                    
                    elif key == 81 or key == ord('['): #left
                        current_index = max(current_index - 1, 0)
                        break
            else:
                break

        # Save all created annotations as a Pascal VOC dataset
        p = pascal_voc.PascalVoc()
        for idx, im in enumerate(all_images):
            if(len(im.annotated_objects) > 0):
                # Load correct image again
                vid.set(cv2.CAP_PROP_POS_FRAMES, idx) 
                ret, frame = vid.read()
                img = cv2.bitwise_and(frame, frame, mask=m.mask)
                p.save(img, im.annotated_objects)

