# -*- coding: utf-8 -*-
# version:python3.6.6
# author:Ivy Wong

# 本循环是对一个大文件夹内的多个小文件夹中的图片进行识别，每个小文件夹为一个csv文件
# 也就是说有两级文件夹目录
# 注意，路径与文件名都不要有中文

# 导入相关模块
import requests
import csv
import time, os
from json import JSONDecoder
from PIL import Image


# 使用face++的api识别情绪
def useapi(img):
    http_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    data = {"api_key":"TmBJ_UuRJyow1PWIjH6iIA3_25a_CIvp",
            "api_secret":"DndanQWy_q2ZIp7iMjMCSIkmdJU6V3Tl",
            "return_attributes": "gender,age,emotion,beauty,smiling,ethnicity,skinstatus"}
    files = {"image_file":open(img, "rb")}
    response = requests.post(http_url, data=data, files=files)
    req_con = response.content.decode('utf-8')
    req_dict = JSONDecoder().decode(req_con)
    print(req_dict)
    return req_dict


# 将json字典写入csv
def detectface(img, temp_data, files_name):
    try:
        parsed = useapi(img)
        if not parsed['faces']:
            print('This picture do not have any face')
        else:
            if len(parsed['faces']) <= 5:  # face++免费版只能识别最多5张人脸
                parsed2 = parsed['faces']
            else:
                parsed2 = parsed['faces'][0:5]
            temp_data = writecsv(temp_data, parsed2, files_name)
        return temp_data
    except Exception as e:
        print(e)
        print('超过了并发数！等一下！')
        time.sleep(3)
        print('The program is going to work')
        detectface(img, temp_data, files_name)


def writecsv(temp_data, parsed2, files_name):
    for list_item in parsed2:
        temp = [0 for i in range(24)]  # 初始化一行，一共有24列
        # 写入文件名
        filename, extension = os.path.splitext(files_name)
        temp[0] = filename

        # 写入时间戳
        daystamp, timestamp, hourstamp = gettimestamp(img)
        temp[1] = daystamp
        temp[2] = timestamp
        temp[3] = hourstamp

        # 写入api返回的数据
        emotion = [0 for i in range(7)]
        for key1, value1 in list_item.items():
            if key1 == 'attributes':
                for key2, value2 in value1.items():
                    if key2 == 'age':
                        temp[5] = value2['value']
                    elif key2 == 'emotion':
                        for key3, value3 in value2.items():
                            if key3 == 'sadness':
                                temp[8] = value3
                                emotion[0] = value3
                            elif key3 == 'neutral':
                                temp[9] = value3
                                emotion[1] = value3
                            elif key3 == 'disgust':
                                temp[10] = value3
                                emotion[2] = value3
                            elif key3 == 'anger':
                                temp[11] = value3
                                emotion[3] = value3
                            elif key3 == 'surprise':
                                temp[12] = value3
                                emotion[4] = value3
                            elif key3 == 'fear':
                                temp[13] = value3
                                emotion[5] = value3
                            else:
                                temp[14] = value3
                                emotion[6] = value3
                    elif key2 == 'gender':
                        temp[6] = value2['value']
                    elif key2 == 'ethnicity':
                        temp[7] = value2['value']
                    elif key2 == 'smile':
                        for key3, value3 in value2.items():
                            if key3 == 'threshold':
                                temp[16] = value3
                            elif key3 == 'value':
                                temp[17] = value3
                            else:
                                pass
                    elif key2 == 'beauty':
                        for key3, value3 in value2.items():
                            if key3 == 'male_score':
                                temp[18] = value3
                            elif key3 == 'female_score':
                                temp[19] = value3
                            else:
                                pass
                    elif key2 == 'skinstatus':
                        for key3, value3 in value2.items():
                            if key3 == 'health':
                                temp[20] = value3
                            elif key3 == 'stain':
                                temp[21] = value3
                            elif key3 == 'acne':
                                temp[22] = value3
                            elif key3 == 'dark_circle':
                                temp[23] = value3
                            else:
                                pass
                    else:
                        pass
            elif key1 == 'face_token':
                temp[4] = value1
            else:
                pass
            temp[15] = emotion.index(max(emotion))
            temp_data.append(temp)

            print('Success! The pic ' + str(files_name) + ' was detected!')

    return temp_data


# 获取图片大小
def imagesize(img):
    Img = Image.open(img)
    w, h = Img.size
    return w,h


# 获取时间戳
def gettimestamp(path):
    statinfo = os.stat(path)
    timeinfo = time.localtime(statinfo.st_mtime)
    daystamp = str(timeinfo.tm_year) + '-' + str(timeinfo.tm_mon) + '-' + str(timeinfo.tm_mday)
    timestamp = str(timeinfo.tm_hour) + ':' + str(timeinfo.tm_min) + ':' + str(timeinfo.tm_sec)
    hourstamp = timeinfo.tm_hour + timeinfo.tm_min / 60.0 + timeinfo.tm_sec / 3600.0
    return daystamp, timestamp, hourstamp


if __name__ == '__main__':
    path = r"D:\temp2" # 需要更改第一级目录
    for root, dirs, files in os.walk(path, topdown=False):
        for folder in dirs:

            print('Let us start dealing with folder ' + folder)

            exec('foldername = open("' + folder + '.csv","w",newline="")')
            # 加上newline参数可以使写的csv文件无空行
            writer = csv.writer(foldername)
            # 设置表头
            title = ['PhotoID', 'daystamp', 'timestamp', 'hourstamp','faceID', 'age', 'gender', 'ethnicity', 'sadness',
                     'neutral','disgust', 'anger', 'surprise', 'fear', 'happiness', 'emotion','smile_threshold','smile_value',
                     'beauty_male','beauty_female','health','stain','acne','dark_circle']
            writer.writerow(title)
            data = []

            # 遍历每个folder里的图片
            for root2, dirs2, files2 in os.walk(path + '\\' + folder):
                for files_name in files2:
                    img = path + '\\' + folder + '\\' + files_name
                    print('Now, the program is going to deal with ' + folder + ' pic' + str(files_name))
                    w,h=imagesize(img)
                    if w < 48 or h < 48 or w > 4096 or h > 4096:  # API对图片大小的限制
                        print('invalid image size')
                    else:
                        data = detectface(img, data, files_name)
            writer.writerows(data)
            foldername.close()
            print('The current folder is done.')

    print('All done!')
