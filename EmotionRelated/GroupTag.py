# coding:utf-8
# version:python3.6.6
# author:Ivy

# 注，最好使用管理员身份运行的cmd运行，使用pycharm等可能会出现卡顿严重之类的情况

import matplotlib.pyplot as plt # plt 用于显示图片
from skimage import io
import pandas as pd


def tagattach(data):
    list = data['PhotoID'].values
    tagdata = []
    for i in range(len(list)):
        if (i != 0) & (list[i] == list[i-1]):
            tagdata.append(group)
            continue
        img=io.imread(ImgPath+'\\'+list[i]+'.jpg')
        io.imshow(img)
        plt.ion()
        plt.pause(0.01)
        flag = input("请输入数字代表group，若为single直接回车:")
        # 1代表group，0代表single
        if not flag:
            group = 0
        else:
            group = 1
        tagdata.append(group)
    return tagdata


if __name__ == '__main__':
    # 设定待处理的文件路径
    ImgPath = r"D:\temp2\temp"
    FilePath = r"D:\temp.csv"
    OutputPath = r"D:\temp_group.csv"

    # 读取数据表
    data = pd.read_csv(FilePath)
    print(data['PhotoID'].values)

    tagdata = tagattach(data)

    data.insert(data.shape[1],'Group',tagdata) # 在最后一列插入group数据
    data.to_csv(OutputPath)

    print("All done!")
