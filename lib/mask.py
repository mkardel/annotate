#!/usr/bin/env python
import os
import cv2
import numpy as np

class Mask:

    def __init__(self, source_video, image):

        # Setup mask_name
        video_name = os.path.basename(source_video)
        name = os.path.splitext(video_name)
        self.mask_name = "mask_{}.png".format(name[0])
        self.points = False
        self.polys = []
        self.image = image
 
        if not os.path.isfile(self.mask_name):
            print("Creating mask for {}".format(source_video))
            self._create_mask()
        else:
            print("Loading mask {}".format(self.mask_name))


        self.mask = cv2.imread(self.mask_name, cv2.CV_8UC1)

    def _clicker_event(self, event, x, y, flags, param):
        # save point to polygon
        if event == cv2.EVENT_LBUTTONDOWN:
            if isinstance(self.points, bool): #first run
                self.points = np.array([ [x,y] ])
            else:
                self.points = np.append(self.points, [[x,y]], axis=0) 
        elif event == cv2.EVENT_RBUTTONDOWN:
            if not isinstance(self.points, bool) and len(self.points) > 0:
                self.points = np.delete(self.points,len(self.points)-1,0)   

    def draw_poly(self, image, pts, col=(255,255,255)):
        cv2.fillConvexPoly(image, pts, col)
        return image

    # Create mask, left mouse adds point, right delete, n adds polygon, d deletes
    def _create_mask(self):

        # Setup window and events
        win_name = 'Create mask'
        create_mask_window = cv2.namedWindow(win_name)
        cv2.setMouseCallback(win_name, self._clicker_event)

        # Loop until mask is created
        while True:
            temp_image = self.image.copy()
            # Draw current points
            if not isinstance(self.points, bool) and len(self.points) > 0:
                temp_image = self.draw_poly(temp_image, self.points)
            # Draw all added polys
            if len(self.polys) > 0:
                for poly in self.polys:
                    temp_image = self.draw_poly(temp_image, poly)

            cv2.imshow(win_name, temp_image)
            key = cv2.waitKey(20) & 0xFF
            # Add new polygon to mask
            if key == ord('n'):
                if not isinstance(self.points, bool):
                    self.polys.append(self.points)
                    self.points = False
            # Delete last polygon
            if key == ord("d"): # delete last polygon
                self.points = False
                if len(self.polys) > 0:
                    self.polys.pop()
            # Finish mask (space)
            if key == 32:
                self._save_mask()
                break
        cv2.destroyWindow(win_name)        

    def _save_mask(self):
        shape = self.image.shape
        # Creates a black image and draws all polynoms onto it.
        mask = np.zeros((shape[0], shape[1]), np.uint8)

        for poly in self.polys:
            mask = self.draw_poly(mask, poly, (255))
        
        cv2.imwrite(self.mask_name, mask)
