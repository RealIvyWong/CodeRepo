# coding:utf-8
# version:python 3.6.6
# author:Ivy

from PIL import Image
import os
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True # 解决image file is truncated异常

# 图片压缩批处理
def compressImage(srcPath,dstPath):
    for filename in os.listdir(srcPath):
        # 如果不存在目的目录则创建一个，保持层级结构
        if not os.path.exists(dstPath):
            os.makedirs(dstPath)

        # 拼接完整的文件或文件夹路径
        srcFile=os.path.join(srcPath,filename)
        dstFile=os.path.join(dstPath,filename)


        # 如果是文件就处理
        if os.path.isfile(srcFile):
            # 打开原图片缩小后保存，可以用if srcFile.endswith(".jpg")或者split，splitext等函数等针对特定文件压缩
            sImg=Image.open(srcFile)
            w,h=sImg.size
            dImg=sImg.resize((w*999//1000,h*999//1000),Image.ANTIALIAS)  # 设置压缩尺寸和选项，注意尺寸要用括号
            dImg.save(dstFile) # 也可以用srcFile原路径保存,或者更改后缀保存，save这个函数后面可以加压缩编码选项JPEG之类的

            # 读取原图片创建时间
            statinfo = os.stat(srcFile)
            ConverTime = statinfo.st_mtime

            # 修改文件时间戳，只能修改【修改时间】与【访问时间】
            times = (ConverTime, ConverTime)
            os.utime(dstFile, times)

            print(dstFile+" compressed succeeded")

        #如果是文件夹就递归
        if os.path.isdir(srcFile):
            compressImage(srcFile,dstFile)

if __name__=='__main__':
    compressImage(r"your origin folder", r"your compressed folder")
    print("All done!")