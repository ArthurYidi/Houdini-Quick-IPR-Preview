# Copyright (C) 2015 Arthur Yidi
# License: BSD Simplified

import os
import hou
import numpy
import time
import tiff

VERBOSE = 0

class IPR():
    def __init__(self, pane, renderTime=1.0):
        self.pane = pane
        self.frames = [1, 240, 1]
        self.renderTime = renderTime

    def setFrameRange(self, start, end, inc=1):
        self.frames = [start, end, inc]

    def saveFrame(self, frame):
        imageRes = self.pane.imageResolution()
        width, height = imageRes[0], imageRes[1]
        pixels = numpy.empty([height, width, 3])
        gamma = 1/2.2

        if VERBOSE:
            startTime = time.time()

        for y in range(height):
            for x in range(width):
                rgba = self.pane.pixel("C", x, (height - 1) - y)
                colors = pixels[y][x]
                for c in range(3):
                    colors[c] = pow(rgba[c], gamma) * 255

        pixels = pixels.astype(numpy.uint8)
        tiff.imsave(hou.expandString('$HIP/render/$HIPNAME.IPR.')
                    + '{:0>4d}'.format(frame) + '.tif', pixels)

        if VERBOSE:
            endTime = time.time()
            elapsedTime = endTime - startTime
            print('Time Saving Pixels: {:.2f}s'.format(elapsedTime))

    def render(self, preview=True):
        renderFolder = hou.getenv('HIP') + '/render'
        if not os.path.exists(renderFolder):
            os.makedirs(renderFolder)

        prevFrame = hou.frame()
        prevDelay = self.pane.delay()
        prevUpdateTime = self.pane.updateTime()
        prevPreview = self.pane.isPreviewOn()

        self.pane.setDelay(0)
        self.pane.setUpdateTime(0.2)
        self.pane.setPreview(preview)

        start = self.frames[0]
        end = self.frames[1] + 1
        inc = self.frames[2]

        for frame in range(start, end, inc):
            hou.setFrame(frame)
            self.pane.resumeRender()
            time.sleep(self.renderTime)
            self.pane.pauseRender()
            self.saveFrame(frame)

        hou.setFrame(prevFrame)
        self.pane.setDelay(prevDelay)
        self.pane.setUpdateTime(prevUpdateTime)
        self.pane.setPreview(prevPreview)

    def profile(self):
        profile(self.render)

def profile(function, args=tuple(), kwargs={}):
    startTime = time.time()
    function(*args, **kwargs)
    endTime = time.time()
    elapsedTime = endTime - startTime
    print('Elapsed Time: {:.2f}s'.format(elapsedTime))
