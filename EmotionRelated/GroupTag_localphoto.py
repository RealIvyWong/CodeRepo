# coding:utf-8
# version:python3.6.6
# author:Ivy

# 注，最好使用pycharm运行
# 用来识别本地图片的数据库，应该有emotion.sqlite与photo.sqlite两个数据库

import matplotlib.pyplot as plt # plt 用于显示图片
import skimage
import numpy as np
import io
import sqlite3
import sys,os


def tag_attach(table,cursor1,cursor2,conn):
    # cursor1是情绪库的游标，cursor2是照片库的游标，conn是情绪库的连接

    # 获取当前表没有打group标签的记录信息
    cursor1.execute("SELECT id,PhotoName FROM {} where tag isNull".format(table))
    face_info1 = cursor1.fetchall()

    print("这张表有{}张人脸需要进行识别".format(len(face_info1)))

    # 获取待打标签的照片的照片名列表
    face_info=np.array(face_info1)
    pn_list=list(np.unique(face_info[:,1]))

    print("但是这张表有{}张照片需要进行识别".format(len(pn_list)))
    print('*******************开始识别{}张照片*******************'.format(len(pn_list)))

    # 开始循环每张照片
    for i in range(len(pn_list)):
        pn=pn_list[i]
        print('正在识别第{}张照片'.format(i+1))
        cursor2.execute("SELECT Data FROM {} WHERE Name='{}'".format(table,pn))
        img=cursor2.fetchall()[0][0]

        img2 = io.BytesIO(img) # 将图片由二进制转换为ByteIO类型
        img3 = skimage.io.imread(img2)
        skimage.io.imshow(img3)
        plt.ion()
        plt.pause(0.01)
        flag = input("请输入数字代表group，若为single直接回车:")
        plt.close()

        # 1代表group，0代表single
        if len(flag)<1:
            groupdata = 0
        else:
            groupdata = 1

        up="UPDATE {} SET tag={} WHERE PhotoName='{}'".format(table,groupdata,pn)
        print(up)
        cursor1.execute(up)
        conn.commit()
        print("照片{} 已经成功打上标签了，这张表还剩{}张".format(tn,len(pn_list)-i-1))


def gettable(cursor):
    # 获取表的名字
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_name1 = cursor.fetchall()
    table_name2 = np.array(table_name1)
    table_name = list(table_name2[:,0])
    for tn in table_name:
        cursor.execute("SELECT tag FROM {} WHERE tag isNull".format(tn))
        l=cursor.fetchall()
        if len(l)>0:
            return tn
    return False

if __name__ == '__main__':

    # 连接两个数据库，emotion.sqlite是情绪数据的数据库，photo是照片数据的数据库
    conn_emotion = sqlite3.connect('emotion.sqlite')
    cur_emotion = conn_emotion.cursor()
    conn_photo = sqlite3.connect('photo.sqlite')
    cur_photo = conn_photo.cursor()

    # 情绪库中每个表一个一个来遍历
    while True:
        tn=gettable(cur_emotion)

        if tn == False:
            print('所有的表都已经处理完了')
            break

        print('现在准备处理{}表'.format(tn))

        tag_attach(tn,cur_emotion,cur_photo,conn_emotion)

    print('恭喜恭喜！全部结束啦！撒花！')
