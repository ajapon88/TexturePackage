# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        TeturePackage
# Purpose:
#
# Author:
#
# Created:     09/04/2014
# Copyright:   (c)  2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import Image

class ImgPlace:
    """ コンストラクタ """
    def __init__(self, x, y, w, h, img=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = img

    """ 点がテクスチャ内にあるかどうか """
    def isInPoint(self, x, y):
        if (self.x < x and x < self.x+self.w and self.y < y and y < self.y+self.h ):
            return True
        return False

    """ テクスチャがかぶっているかどうか """
    def isConflictPlace(self, place):
        if (self.isInPoint(place.x, place.y)):
            return True
        if (self.isInPoint(place.x+place.w, place.y)):
            return True
        if (self.isInPoint(place.x, place.y+place.h)):
            return True
        if (self.isInPoint(place.x+place.w, place.y+place.h)):
            return True
        if (place.isInPoint(self.x, self.y)):
            return True
        if (place.isInPoint(self.x+self.w, self.y)):
            return True
        if (place.isInPoint(self.x, self.y+self.h)):
            return True
        if (place.isInPoint(self.x+self.w, self.y+self.h)):
            return True
        return False


class PackTexture:
    """ コンストラクタ """
    def __init__(self):
        self.width = 0
        self.height = 0
        self.images = []

    """ テクスチャを隙間に追加 """
    """ 追加できなたらTrueを返す """
    def fillSpaceImage(self, image):
        # 追加済みテクスチャの左下、右下、右上を起点としてテクスチャを置く
        for packimg in self.images:
            x = packimg.x+packimg.w
            y = packimg.y
            if (self.fitImageTest(x, y, image.size[0], image.size[1])):
                self.images.append(ImgPlace(x, y, image.size[0], image.size[1], image))
                return True
            x = packimg.x
            y = packimg.y+packimg.h
            if (self.fitImageTest(x, y, image.size[0], image.size[1])):
                self.images.append(ImgPlace(x, y, image.size[0], image.size[1], image))
                return True
            x = packimg.x+packimg.w
            y = packimg.y+packimg.h
            if (self.fitImageTest(x, y, image.size[0], image.size[1])):
                self.images.append(ImgPlace(x, y, image.size[0], image.size[1], image))
                return True
        return False

    """ はめ込みテスト """
    def fitImageTest(self, x, y, w, h):
        # テクスチャサイズチェック
        if (x+w > self.width or y+h > self.height):
            return False
        # 追加済みのテクスチャとかぶっているかどうか
        place = ImgPlace(x, y, w, h)
        for packimg in self.images:
            if (place.isConflictPlace(packimg)):
                return False
        return True

    """ テクスチャを拡張して追加 """
    def expendSpaceImage(self, image):
        # とりあえず横に拡張して追加
        self.images.append(ImgPlace(self.width, 0, image.size[0], image.size[1], image))
        self.width += image.size[0]
        self.height = max(self.height, image.size[1])


    """ テクスチャ生成 """
    def exportTexture(self, path):
        if (self.width <= 0 or self.height <= 0):
            return
        img = Image.new("RGBA", (self.width, self.height))
        for packimg in self.images:
            img.paste(packimg.img, (packimg.x, packimg.y))
        img.save(path)


""" テクスチャサイズソート """
def imagesizecomp(a, b):
    asize = a.size[0]*a.size[1]
    bsize = b.size[0]*b.size[1]
    if (asize < bsize):
        return 1
    if (asize > bsize):
        return -1
    return 0

def main(pakimglist):
    imglist = []
    for imgname in pakimglist:
        imglist.append(Image.open(imgname))

    # 大きい順にソート
    imglist.sort(cmp=imagesizecomp)

    # 追加
    packtexture = PackTexture()
    while len(imglist) > 0:
        fill = False
        for img in imglist:
            if (packtexture.fillSpaceImage(img)):
                imglist.remove(img)
                fill = True
                break
        if (not fill):
            packtexture.expendSpaceImage(imglist[0])
            imglist.pop(0)

    packtexture.exportTexture('export.png')

if __name__ == '__main__':
    main(['01.png', '02.png', '03.png'])
