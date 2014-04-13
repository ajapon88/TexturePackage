# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        CreateTexture
# Purpose:
#
# Author:
#
# Created:     09/04/2014
# Copyright:   (c)  2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
import os
import random
import Image
import ImageDraw
import ImageFont

if __name__ == '__main__':
    maxsize=300
    minsize=10
    num=10

    output_dir = 'Images'

    if (not os.path.isdir(output_dir)):
        os.mkdir(output_dir)
    os.chdir(output_dir)
    for n in range(0, num):
        w = random.randint(minsize, maxsize)
        h = random.randint(minsize, maxsize)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        img = Image.new("RGB", (w, h), (r, g, b))

        draw = ImageDraw.Draw(img)
        x = w/2-2
        y = h/2-4
        draw.text((x+1, y+1), '%d'%n, (255, 255, 255))
        draw.text((x+1, y-1), '%d'%n, (255, 255, 255))
        draw.text((x-1, y+1), '%d'%n, (255, 255, 255))
        draw.text((x-1, y-1), '%d'%n, (255, 255, 255))
        draw.text((x, y), '%d'%n, (0, 0, 0))

        img.save('%d.png'%n)
