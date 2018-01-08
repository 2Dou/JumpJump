#!/usr/bin/python
#encoding: utf-8

from PIL import Image as PImage
from PIL import ImageDraw as PImageDraw

class Image(object):
    """
    """
    def __init__(self, file = None):
        if file is not None:
            self.file_ = file
            self.img_ = PImage.open(file)
            self.img_draw_ = PImageDraw.Draw(self.img_)
            self.width = self.img_.size[0]
            self.height = self.img_.size[1]
        else:
            self.img_ = None
            self.img_draw_ = None

    def getpixel(self, pt):
        return self.img_.getpixel(pt)

    def line(self, pt1, pt2, color=(255, 0, 0), width = 1):
        self.img_draw_.line(pt1 + pt2, fill=color, width = width)

    def mark(self, pt, text, color=(255, 0, 0), width = 1):
        self.line(pt, pt)
        self.img_draw_.text([pt[0]+2, pt[1]], text, fill=color)

    def close(self):
        del self.img_draw_
        self.img_.close()

        self.img_ = None
        self.img_draw_ = None

    def save(self):
        self.img_.save(self.file_)
