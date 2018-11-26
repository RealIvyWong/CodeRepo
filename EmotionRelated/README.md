# 情绪研究相关的代码

本文件夹主要是放目前在做的情绪研究相关的代码，主要是python语言的。



## sqlite_localphoto.py

该文件是将本地图片数据存储在本地的sqlite数据库中，如果图片大小或长宽不符合face++的要求，将进行压缩存储。

写出来的数据库应该是下图这样的

![1543230617259](D:\10GitRepository\CodeRepo\EmotionRelated\assets\1543230617259.png)

## GroupTag_localphoto.py

需要emotion.sqlite和photo.sqlite两个数据库。向emotion库写入group的标签。适用于本地照片的数据库。网络照片可能会有字段不匹配的问题。

大概的运行场景如下图所示（当然还是推荐使用pycharm，不然可能会存在输入光标不会保持在命令行中的情况）

![1543230820411](D:\10GitRepository\CodeRepo\EmotionRelated\assets\1543230820411.png)



## LocalEmotion.py

识别本地照片库的情绪。使用face++ API。

运行情况大概如下图所示

![1543238320038](D:\10GitRepository\CodeRepo\EmotionRelated\assets\1543238320038.png)

生成的数据库大概是下图这样

![1543238406149](D:\10GitRepository\CodeRepo\EmotionRelated\assets\1543238406149.png)

## WeiboEmotion

使用face++ API识别微博图片的情绪。

和LocalEmotion.py最主要的区别是传入的是图片的url，所以使用了face++的Python SDK（稍微做了一点点修改）。

里面还有个代码testone.py是用来测试单张图片URL的。



## LocalFile_testone.py

用来测试本地单张图片使用face++ API返回情况的。



## mysql_cloudphoto.py

用来将本地图片上传到云数据库mysql中。

还不成熟，以后再改。



## CloudEmotion.py

用云主机和云数据库mysql中的数据来识别情绪。

还不成熟，以后再改。