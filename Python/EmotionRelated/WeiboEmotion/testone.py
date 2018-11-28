# -*- coding: utf-8 -*-
# version:python3.6.6
# author:Ivy Wong

from PythonSDK.facepp import API

if __name__ == '__main__':
    # 添加API Key API Secret
    API_KEY = 'TmBJ_UuRJyow1PWIjH6iIA3_25a_CIvp'
    API_SECRET = 'DndanQWy_q2ZIp7iMjMCSIkmdJU6V3Tl'

    api=API(API_KEY,API_SECRET)
    detech_img_url='https://wx1.sinaimg.cn/large/ae33a3b3gy1fxgntfe6psj23342bcu11.jpg'
    res = api.detect(image_url=detech_img_url, return_attributes="gender,age,emotion,beauty,smiling,ethnicity,skinstatus")
    print(res)
