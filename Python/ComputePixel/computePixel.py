# coding:utf-8
# version:python3.7
# author:Ivy

# 实现计算图片中各个颜色的像素的数量与占比

from PIL import Image

#####################
### 设置区
#####################

file=r'C:\Users\Ivy\Pictures\42825492.jpg' # 图片路径

######################

# 计算各个颜色的占比
def countAll(file):
    im = Image.open(file)
    w = im.size[0]
    h = im.size[1]
    im = im.convert('RGB')
    all = w*h
    colorList=[]
    colorDict={}
    for x in range(w):
        for y in range(h):
            # 循环每一个像素点
            rgb = im.getpixel((x,y))
            # 如果这个颜色没有记录过
            if rgb not in colorList:
                colorList.append(rgb)
                colorDict[rgb]=0

            colorDict[rgb]+=1

    return colorDict

colorDict=countAll(file)
print('计算完毕，开始打印')
for (k,v) in colorDict.items():
    print(k,v)
