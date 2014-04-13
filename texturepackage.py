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
import sys
import os.path
import time
import glob
import Image
import xml.dom.minidom

""" テクスチャ配置クラス """
class ImgPlace:
    NOROTATE = 0
    ROTATE = 1
    """ コンストラクタ """
    def __init__(self, x, y, w, h, r=NOROTATE, img=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.r = r
        self.img = img

    """ 点がテクスチャ内にあるかどうか """
    def isInPoint(self, x, y):
        if (self.x <= x and x <= self.x+self.w-1 and self.y <= y and y <= self.y+self.h-1 ):
            return True
        return False

    """ テクスチャがかぶっているかどうか """
    def isConflictPlace(self, place):
        # 範囲外かどうかで判定
        if (place.x+place.w-1 < self.x):
            return False
        if (self.x+self.w-1 < place.x):
            return False
        if (place.y+place.h-1 < self.y):
            return False
        if (self.y+self.h-1 < place.y):
            return False
        return True


""" テクスチャパッククラス """
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
            places = [
                # 無回転
                ImgPlace(packimg.x+packimg.w, packimg.y,           image.size[0], image.size[1], ImgPlace.NOROTATE),
                ImgPlace(packimg.x,           packimg.y+packimg.h, image.size[0], image.size[1], ImgPlace.NOROTATE),
                ImgPlace(packimg.x+packimg.w, packimg.y+packimg.h, image.size[0], image.size[1], ImgPlace.NOROTATE),
                # 回転
                ImgPlace(packimg.x+packimg.w, packimg.y,           image.size[1], image.size[0], ImgPlace.ROTATE),
                ImgPlace(packimg.x,           packimg.y+packimg.h, image.size[1], image.size[0], ImgPlace.ROTATE),
                ImgPlace(packimg.x+packimg.w, packimg.y+packimg.h, image.size[1], image.size[0], ImgPlace.ROTATE),
            ]
            for p in places:
                if (self.fitImageTest(p.x, p.y, p.w, p.h)):
                    if (p.r == ImgPlace.ROTATE):
                        p.img = image.transpose(Image.ROTATE_90)
                    else:
                        p.img = image
                    self.images.append(p)
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
        if self.height < self.width:
            x = 0
            y = self.height
            w = max(self.width, image.size[0])
            h = self.height + image.size[1]
            rw = max(self.width, image.size[1])
            rh = self.height + image.size[0]
        else:
            x = self.width
            y = 0
            w = self.width + image.size[0]
            h = max(self.height, image.size[1])
            rw = self.width + image.size[1]
            rh = max(self.height, image.size[0])
        if (rw*rh >= w*h):
            self.images.append(ImgPlace(x, y, image.size[0], image.size[1], ImgPlace.NOROTATE, image))
            self.width = w
            self.height = h
        else:
            self.images.append(ImgPlace(x, y, image.size[1], image.size[0], ImgPlace.ROTATE, image.transpose(Image.ROTATE_90)))
            self.width = rw
            self.height = rh

    """ テクスチャ生成 """
    def exportTexture(self, path):
        if (self.width <= 0 or self.height <= 0):
            return
        img = Image.new("RGBA", (self.width, self.height))
        for packimg in self.images:
            img.paste(packimg.img, (packimg.x, packimg.y))
        img.save(path)

    """ テクスチャDict作成 """
    def createTextureInfoDict(self, imgplace):
        doc = xml.dom.minidom.Document()
        dict = doc.createElement('dict')
        # frame
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('frame'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode('{{%d,%d},{%d,%d}'%(imgplace.x,imgplace.y,imgplace.w,imgplace.h)))
        dict.appendChild(key)
        dict.appendChild(data)
        # offset
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('offset'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode('{0,0}'))
        dict.appendChild(key)
        dict.appendChild(data)
        # rotated
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('rotated'))
        if (imgplace.r == ImgPlace.ROTATE):
            data = doc.createElement('true')
        else:
            data = doc.createElement('false')
        dict.appendChild(key)
        dict.appendChild(data)
        """
        # よくわからないので保留
        # sourceColorRect
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('sourceColorRect'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode('{{0,0},{0,0}}'))
        dict.appendChild(key)
        dict.appendChild(data)
        """
        # offset
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('sourceSize'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode('{%d,%d}'%(imgplace.w, imgplace.h)))
        dict.appendChild(key)
        dict.appendChild(data)

        return dict

    """ Metadata Dict作成 """
    def createMetadataDict(self, texturename):
        doc = xml.dom.minidom.Document()
        dict = doc.createElement('dict')
        # format
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('format'))
        data = doc.createElement('integer')
        data.appendChild(doc.createTextNode('2'))
        dict.appendChild(key)
        dict.appendChild(data)
        # realTextureFileName
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('realTextureFileName'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode(texturename))
        dict.appendChild(key)
        dict.appendChild(data)
        # size
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('size'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode('{%d,%d}'%(self.width,self.height)))
        dict.appendChild(key)
        dict.appendChild(data)
        # smartupdate
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('smartupdate'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode(''))
        dict.appendChild(key)
        dict.appendChild(data)
        # textureFileName
        key = doc.createElement('key')
        key.appendChild(doc.createTextNode('textureFileName'))
        data = doc.createElement('string')
        data.appendChild(doc.createTextNode(texturename))
        dict.appendChild(key)
        dict.appendChild(data)

        return dict


    """ plist作成 """
    def exportPlist(self, texturepath):
        texturename = os.path.basename(texturepath)
        texturenameroot, ext = os.path.splitext(texturename)
        plistname = os.path.dirname(texturepath) + texturenameroot + '.plist'
        doc = xml.dom.minidom.Document()
        root = doc.createElement('plist')
        root.setAttribute('version', '1.0')
        doc.appendChild(root)
        rootdict = doc.createElement('dict')
        root.appendChild(rootdict)
        frame_key = doc.createElement('key')
        frame_key.appendChild(doc.createTextNode('frames'))
        frames = doc.createElement('dict')
        rootdict.appendChild(frame_key)
        rootdict.appendChild(frames)
        for packimg in self.images:
            key = doc.createElement('key')
            key.appendChild(doc.createTextNode('filename'))
            frames.appendChild(key)
            frames.appendChild(self.createTextureInfoDict(packimg))
        metadata_key = doc.createElement('key')
        metadata_key.appendChild(doc.createTextNode('metadata'))
        rootdict.appendChild(metadata_key)
        rootdict.appendChild(self.createMetadataDict(texturename))

        f = open(plistname, 'w')
        f.write(doc.toprettyxml('    ', '\n', 'utf-8'))
        f.close()


""" テクスチャサイズソート """
def lessImageSize(a, b):
    asize = a.size[0]*a.size[1]
    bsize = b.size[0]*b.size[1]
    if (asize < bsize):
        return 1
    if (asize > bsize):
        return -1
    return 0

""" テクスチャパック """
def texturepackage(pakimglist, output):
    imglist = []
    for imgname in pakimglist:
        try:
            img = Image.open(imgname)
            if img:
                img.filename = imgname
                imglist.append(img)
        except:
            print 'Image open error. \'%s \'' % imgname
    # 大きい順にソート
    imglist.sort(cmp=lessImageSize)

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
#        packtexture.exportTexture('export%d.png'%len(imglist))

    packtexture.exportTexture(output)
    packtexture.exportPlist(output)

""" usage """
def usage():
    print 'usage: %s image_files... output' % sys.argv[0]

if __name__ == '__main__':
    argv = sys.argv
    argv.pop(0)
    argc = len(argv)
    if (argc > 1):
        output = argv[argc-1]
        argv.pop(argc-1)
        files = []
        for f in argv:
            files += glob.glob(f)
        if (len(files) <= 0):
            print 'No input files.'
            exit(1)
        print 'Input %d files.' % len(files)
        if (open(output, 'w')):
            t0 = time.time()
            texturepackage(files, output)
            print 'Process time:%ssec' % round(time.time()-t0, 3)
        else:
            print 'Output file open error. \'%s\'' % output
            exit(1)
    else:
        usage()

