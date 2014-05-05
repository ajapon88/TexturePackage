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
                        p.img = image.transpose(Image.ROTATE_270)
                        p.img.filename = image.filename
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
            rotimg = image.transpose(Image.ROTATE_270)
            rotimg.filename = image.filename
            self.images.append(ImgPlace(x, y, image.size[1], image.size[0], ImgPlace.ROTATE, rotimg))
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

    """ Key-Data追加 """
    def addElemKeyData(self, elem, key, data, value=None):
        doc = xml.dom.minidom.Document()
        elem_key = doc.createElement('key')
        elem_key.appendChild(doc.createTextNode(key))
        elem_data = doc.createElement(data)
        if (value is not None):
            elem_data.appendChild(doc.createTextNode(value))
        elem.appendChild(elem_key)
        elem.appendChild(elem_data)

    """ Key-Element追加 """
    def addElemKeyElement(self, elem, key, data):
        doc = xml.dom.minidom.Document()
        elem_key = doc.createElement('key')
        elem_key.appendChild(doc.createTextNode(key))
        elem.appendChild(elem_key)
        elem.appendChild(data)

    """ テクスチャDict作成 """
    def createTextureInfoDict(self, imgplace):
        doc = xml.dom.minidom.Document()
        dict = doc.createElement('dict')
        # frame
        if (imgplace.r == ImgPlace.ROTATE):
            self.addElemKeyData(dict, 'frame', 'string', '{{%d,%d},{%d,%d}}'%(imgplace.x,imgplace.y,imgplace.h,imgplace.w))
        else:
            self.addElemKeyData(dict, 'frame', 'string', '{{%d,%d},{%d,%d}}'%(imgplace.x,imgplace.y,imgplace.w,imgplace.h))
        # offset
        self.addElemKeyData(dict, 'offset', 'string', '{0,0}')
        # rotated
        if (imgplace.r == ImgPlace.ROTATE):
            self.addElemKeyData(dict, 'rotated', 'true')
        else:
            self.addElemKeyData(dict, 'rotated', 'false')
        # sourceColorRect
        # よくわからないので保留
        # self.addElemKeyData(dict, 'sourceColorRect', 'string', '{{0,0},{0,0}}')
        # sourceSize
        self.addElemKeyData(dict, 'sourceSize', 'string', '{%d,%d}'%(imgplace.w, imgplace.h))

        return dict

    """ Metadata Dict作成 """
    def createMetadataDict(self, texturename):
        doc = xml.dom.minidom.Document()
        dict = doc.createElement('dict')
        # format
        # 2にのみ対応
        self.addElemKeyData(dict, 'format', 'integer', '2')
        # realTextureFileName
        self.addElemKeyData(dict, 'realTextureFileName', 'string', texturename)
        # size
        self.addElemKeyData(dict, 'size', 'string', '{%d,%d}'%(self.width,self.height))
        # smartupdate
        """
        self.addElemKeyData(dict, 'smartupdate', 'string', '')
        """
        # textureFileName
        self.addElemKeyData(dict, 'textureFileName', 'string', texturename)

        return dict


    """ plist作成 """
    def exportPlist(self, plistpath, texturename):
        doc = xml.dom.minidom.Document()

        plist = doc.createElement('plist')
        plist.setAttribute('version', '1.0')
        doc.appendChild(plist)

        rootdict = doc.createElement('dict')
        plist.appendChild(rootdict)

        frames = doc.createElement('dict')
        for packimg in self.images:
            self.addElemKeyElement(frames, packimg.img.filename, self.createTextureInfoDict(packimg))
        self.addElemKeyElement(rootdict, 'frames', frames)
        self.addElemKeyElement(rootdict, 'metadata', self.createMetadataDict(texturename))

        f = open(plistpath, 'w')
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
def texturepackage(pakimglist, outputtex, outputplist):
    imglist = []
    for imgname in pakimglist:
        try:
            img = Image.open(imgname)
            if img:
                # ひとまずファイル名を無理やり持たせる
                img.filename = os.path.basename(imgname)
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

    packtexture.exportTexture(outputtex)
    packtexture.exportPlist(outputplist, outputtex)

""" usage """
def usage():
    print 'usage: %s image_files... output' % sys.argv[0]

if __name__ == '__main__':
    argv = sys.argv
    argv.pop(0)
    argc = len(argv)
    if (argc > 1):
        output = os.path.abspath(argv[argc-1])
        argv.pop(argc-1)
        files = []
        for f in argv:
            files += glob.glob(f)
        if (len(files) <= 0):
            print 'No input files.'
            exit(1)
        print 'Input %d files.' % len(files)
        outputfile = os.path.basename(output)
        outputfilebase, ext = os.path.splitext(outputfile)
        if ext == '':
            ext = '.png'
        outputbase = os.path.dirname(output) + os.sep + outputfilebase
        outputtex = outputbase + ext
        outputplist = outputbase + '.plist'
        if (not open(outputtex, 'w')):
            print 'Output file open error. \'%s\'' % outputtex
            exit(1)
        elif (not open(outputplist, 'w')):
            print 'Output file open error. \'%s\'' % outputplist
            exit(1)
        else:
            t0 = time.time()
            texturepackage(files, outputtex, outputplist)
            print 'Output texture path \'%s\'' % outputtex
            print 'Output plist path \'%s\'' % outputplist
            print 'Process time:%ssec' % round(time.time()-t0, 3)
    else:
        usage()

