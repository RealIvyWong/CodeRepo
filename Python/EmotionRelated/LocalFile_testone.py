# -*- coding: utf-8 -*-
# version:python3.6.6
# author:Ivy Wong

import requests
from json import JSONDecoder

def useapi(img):
    http_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    data = {"api_key":"TmBJ_UuRJyow1PWIjH6iIA3_25a_CIvp",
            "api_secret":"DndanQWy_q2ZIp7iMjMCSIkmdJU6V3Tl",
            "return_attributes": "gender,age,emotion,beauty,smiling,ethnicity,skinstatus"}
    files = {"image_file":open(img, "rb")}
    response = requests.post(http_url, data=data, files=files)
    req_con = response.content.decode('utf-8')
    req_dict = JSONDecoder().decode(req_con)
    return req_dict

if __name__ == '__main__':
    img  = 'D:/EmotionRawData/weibo/1007/1010.JPG'
    parsed = useapi(img)
    print(parsed)
