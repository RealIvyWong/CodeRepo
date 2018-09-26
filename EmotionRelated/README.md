# 情绪研究相关的代码

本文件夹主要是放目前在做的情绪研究相关的代码，主要是python语言的。



## detectemotion_azure.py

该文件是使用Microsoft Azure的人脸API进行情绪识别的代码，因为个人需要，设置成了双层目录读取的结构。最后生成的是一个csv文件。

由于本人的免费key已经过期，所以还没测试过是否有bug，如有麻烦联系一下。

## detectemotion_facepp.py

该文件是使用face++的人脸识别API进行情绪识别的代码，因为个人需要，设置成了双层目录读取的结构。最后生成的是一个csv文件。

## CompressImage.py

该文件是将图像进行压缩的代码，因为face++对图片大小有限制，所以可能会需要使用到该代码。