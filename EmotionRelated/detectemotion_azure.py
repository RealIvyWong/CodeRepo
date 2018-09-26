# coding:utf-8
# version:python3.6.6
# author:Ivy Wong

# 本循环是对一个大文件夹内的多个小文件夹中的图片进行识别，每个小文件夹为一个csv文件
# 也就是说有两级文件夹目录
# 注意，路径与文件名都不要有中文

# 导入相关模块
import urllib, json
import urllib.parse, urllib.error, http.client
import urllib.request
import csv
import time, os


# 使用micrsoft的api识别情绪
def useapi(img_path):
    # 定义html的header，这里Content-type决定了body中的类型，/json是URL模式,/octet-stream是本地模式
    headers = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '3a6e55cfe5ad46a1a5d1e6731214aada',
    }

    # 定义返回的内容，包括FaceId，年龄、性别等等
    params = urllib.parse.urlencode({
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
        'returnFaceAttributes': 'age,gender,smile,facialHair,glasses,emotion,makeup',
    })

    img = open(os.path.expanduser(img_path), 'rb')  # 打开图片文件

    # Call Face API，进行人脸识别
    try:
        # Execute the REST API call and get the response.
        conn = http.client.HTTPSConnection('api.cognitive.azure.cn')
        conn.request("POST", "/emotion/v1.0/recognize?%s" % params, img, headers)
        response = conn.getresponse()
        data = response.read()

        # 'data' contains the JSON data. The following formats the JSON data for display.
        parsed = json.loads(data)
        conn.close()

    except Exception as e:
        print(e.args)

    return parsed


# 将json字典写入csv
# 变量用来循环时控制写入单元格，感觉有更好的表达方式

def writecsv(temp_data, files_name, img_path, file_num):
    parsed = useapi(img_path)
    if not parsed:
        print('这张图片没有任何人脸')
    elif 'error' in parsed:
        print(parsed['error']['message'])
        if parsed['error']['message'] == 'Rate limit is exceeded. Try again later.':
            print('文件编号是 ' + str(file_num))
            print('程序将暂停60s')
            time.sleep(60)
            print('程序将继续开始工作啦')
            writecsv(worksheet, files_name, img_path, file_num)
    else:
        for list_item in parsed:
            temp = [0 for i in range(23)]  # 初始化一行，一共有23列
            filename, extension = os.path.splitext(files_name)
            temp[0] = filename

            # 写入时间戳
            daystamp, timestamp, hourstamp = gettimestamp(img_path)
            temp[1] = daystamp
            temp[2] = timestamp
            temp[3] = hourstamp

            # 写入api返回的数据
            emotion = [0 for i in range(7)]
            for key1, value1 in list_item.items():
                if key1 == 'faceAttributes':
                    for key2, value2 in value1.items():
                        if key2 == 'age':
                            temp[5] = value2
                        elif key2 == 'emotion':
                            for key3, value3 in value2.items():
                                if key3 == 'anger':
                                    temp[8] = value3
                                    emotion[0] = value3
                                elif key3 == 'contempt':
                                    temp[9] = value3
                                    emotion[1] = value3
                                elif key3 == 'disgust':
                                    temp[10] = value3
                                    emotion[2] = value3
                                elif key3 == 'fear':
                                    temp[11] = value3
                                    emotion[3] = value3
                                elif key3 == 'happiness':
                                    temp[12] = value3
                                    emotion[4] = value3
                                elif key3 == 'neutral':
                                    temp[13] = value3
                                    emotion[5] = value3
                                elif key3 == 'sadness':
                                    temp[14] = value3
                                    emotion[6] = value3
                                else:
                                    temp[15] = value3
                                    emotion[7] = value3
                        elif key2 == 'gender':
                            temp[6] = value2
                        elif key2 == 'glasses':
                            temp[7] = value2
                        elif key2 == 'makeup':
                            for key3, value3 in value2.items():
                                if key3 == 'lipMakeup':
                                    temp[17] = value3
                                elif key3 == 'eyeMakeup':
                                    temp[18] = value3
                                else:
                                    pass
                        elif key2 == 'facialHair':
                            if key3 == 'sideburns':
                                temp[19] = value3
                            elif key3 == 'moustache':
                                temp[20] = value3
                            elif key3 == 'beard':
                                temp[21] = value3
                            else:
                                pass
                        else:
                            pass
                elif key1 == 'faceId':
                    temp[4] = value1
                else:
                    pass
            temp[16] = emotion.index(max(emotion))
            temp_data.append(temp)
            print('Success! The pic ' + str(files_name) + ' was detected!')
    return temp_data


# 获取时间戳
def gettimestamp(path):
    statinfo = os.stat(path)
    timeinfo = time.localtime(statinfo.st_mtime)
    daystamp = str(timeinfo.tm_year) + '-' + str(timeinfo.tm_mon) + '-' + str(timeinfo.tm_mday)
    timestamp = str(timeinfo.tm_hour) + ':' + str(timeinfo.tm_min) + ':' + str(timeinfo.tm_sec)
    hourstamp = timeinfo.tm_hour + timeinfo.tm_min / 60.0 + timeinfo.tm_sec / 3600.0
    return daystamp, timestamp, hourstamp


if __name__ == '__main__':
    path = r'your first folder" # 需要更改的第一级目录'
    for root, dirs, files in os.walk(path, topdown=False):
        for folder in dirs:

            print('Let us start dealing with folder ' + folder)

            exec('foldername = open("' + folder + '.csv","w",newline="")')
            # 加上newline参数可以使写的csv文件无空行
            writer = csv.writer(foldername)
            # 设置表头
            title = ["PhotoID", "daystamp", "timestamp", "hourstamp", "faceID", "age", "gender", "glasses",
                          "anger", "contempt", "disgust", "fear", "happiness", "neutral", "sadness", "surprise",
                          "emotion", "lipMakeup", "eyeMakeup", "sideburns", "moustache", "bread"]

            writer.writerow(title)
            data = []

            # 遍历每个folder里的图片
            file_num = 1
            for root2, dirs2, files2 in os.walk(path + '\\' + folder):
                for files_name in files2:

                    try:
                        img_path = path + '\\' + folder + '\\' + files_name
                        print('Now, the program is going to deal with ' + folder + ' pic' + str(files_name))
                        data = writecsv(data, files_name, img_path, file_num)
                        file_num += 1
                    except Exception as e:
                        print(e)

            print('The current folder is done.')
            writer.writerows(data)
            foldername.close()

    print('The program is done!')