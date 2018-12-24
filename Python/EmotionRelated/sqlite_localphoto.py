# -*- coding: utf-8 -*-
# version:python3.7
# author:Ivy Wong

# 这个程序用来将第一级目录下所有第二级目录里的图片写入照片数据库

import sys
import os.path
import sqlite3
import io
import os
import math
# 需要额外安装的包
import exifread
from PIL import Image

# 自己设置区
path = "D:/emotionrawdata/urban" # 第一级目录
threshold_size = 2 # 设置最大的图片大小，单位为M
db_path = 'photo.sqlite'

def uploadimg(folder,filename,photo,photo_resize):
    try:
        add_row="INSERT INTO pic(PhotoName, daystamp, timestamp, hourstamp, place, pid, Data) VALUES(?,?,?,?,?,?,?)"
        daystamp, timestamp, hourstamp = gettimestamp(photo)
        pid=folder+'-'+filename
        cur.execute(add_row, (filename, daystamp, timestamp, hourstamp, folder,pid, photo_resize))
        conn.commit()
    except Exception as e:
        print(e)
        sys.exit(1)


def createtable():
    create_table='''CREATE TABLE IF NOT EXISTS pic(Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                                    PhotoName TEXT,
                                    daystamp TEXT,
                                    timestamp TEXT,
                                    hourstamp REAL,
                                    place TEXT,
                                    Data BLOB NOT NULL)'''
    cur.execute(create_table)
    conn.commit()


# 获取时间戳
def gettimestamp(img):
    try:
        img2 = io.BytesIO(img) # 将图片由二进制转换为ByteIO类型
        tags = exifread.process_file(img2)
        date=tags["EXIF DateTimeOriginal"].printable
        daystamp, timestamp=date.split()
        h,m,s=timestamp.split(':')
        h = int(h)
        m = int(m)
        s = int(s)
        hourstamp = h + m / 60.0 + s / 3600.0
        return daystamp, timestamp, hourstamp
    except:
        print('Timestamp invalid!')
        return str(0),str(0),0

# 调整图片大小至2m
def resize_images(img):
    filesize = os.path.getsize(img) # 大小
    with Image.open(img) as im:
        w, h = im.size
        if filesize > threshold: # 判断图片文件大小是否符合阈值
            if w >= h:
                new_w= int(math.sqrt(threshold/2))
                new_h = int(new_w * h * 1.0 / w)
            else:
                new_h = int(math.sqrt(threshold/2))
                new_w = int(new_h * w * 1.0 / h)
            resized_im = im.resize((new_w, new_h))
            resized_im.save('temp.jpg')
            img = 'temp.jpg'
            print('太大了！压缩一下！')

    with Image.open(img) as im:
        w, h = im.size
        if w < 48 or h < 48: # 判断图片长宽大小是否符合最小阈值
            print('Image is too small. Next!')
            return False
        elif w > 4096 or h > 4096: # 判断图片长宽大小是否符合最大阈值
            if w >= h:
                new_w = 4096
                new_h = int(new_w * h * 1.0 / w)
            else:
                new_h = 4096
                new_w = int(new_h * w * 1.0 / h)
            resized_im = im.resize((new_w, new_h))
            resized_im.save('temp2.jpg')
            img = 'temp2.jpg'
            print('长宽不对！压缩一下！')

    f2 = open(img,'rb')
    photo_resize = f2.read()
    f2.close()

    if os.path.exists('temp.jpg'):
        os.remove('temp.jpg')
    elif os.path.exists('temp2.jpg'):
        os.remove('temp2.jpg')
    else:
        pass

    return photo_resize


if  __name__ == '__main__':

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 初始化数据库
    createtable()

    threshold = threshold_size*1024*1024
    for root, dirs, files in os.walk(path, topdown=False):
        for folder in dirs:

            print('开始上传文件夹',folder)


            for root2, dirs2, files2 in os.walk(path + '/' + folder):

                # 判断这个文件夹是不是上传完了
                cur.execute('select * from pic where place="{}"'.format(folder))
                folder_info=cur.fetchall()
                if len(folder_info)==len(files2):
                    print('这个文件夹上传过了！')
                    break

                # 遍历每个folder里的图片
                for files_name in files2:
                    img = path + '/' + folder + '/' + files_name

                    print('现在开始上传文件夹{}的照片{}'.format(folder,files_name))

                    # 判断是不是上传过这张照片
                    cur.execute('select * from pic where PhotoName="{}" and place="{}"'.format(files_name,folder))
                    info=cur.fetchall()
                    if len(info)>0:
                        print('这张图片上传过了！')
                        continue

                    # 二进制打开原始图片
                    f = open(img,'rb')
                    photo = f.read()
                    f.close()

                    # 压缩图片
                    photo_resize = resize_images(img)

                    uploadimg(folder,files_name,photo,photo_resize)

                    print('文件夹{}的照片{}已经上传成功了！'.format(folder,files_name))

                print('文件夹{}上传完了！'.format(folder))

    print('All done!')
    cur.close()
    conn.close()
