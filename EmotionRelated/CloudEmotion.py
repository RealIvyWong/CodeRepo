# -*- coding: utf-8 -*-
# version:python3.7.0
# author:Ivy Wong

# 用来识别云数据库中的图片的情绪
# 还不成熟，以后再改

# 导入相关模块
import requests
import pymysql
import sys
import csv
from json import JSONDecoder
from PIL import Image
import random
import yagmail
import io
import exifread

# 使用face++的api识别情绪
def useapi(img):
    http_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"

    proxy_url=random_ip()

    data = {"api_key":"TmBJ_UuRJyow1PWIjH6iIA3_25a_CIvp",
            "api_secret":"DndanQWy_q2ZIp7iMjMCSIkmdJU6V3Tl",
            "return_attributes": "gender,age,emotion,beauty,smiling,ethnicity,skinstatus"}
    files = {"image_file":img}
    response = requests.post(http_url, data=data, files=files, proxies=proxy_url)
    req_con = response.content.decode('utf-8')
    req_dict = JSONDecoder().decode(req_con)
    return req_dict

# 随机选择一个代理
def random_ip():
    num = random.randint(0,4) #随机选一个0到4的整数
    # 注意代理池可能需要更新
    ip_pool=[{},{"http" : "118.190.95.35:9001"},{"http":"106.75.164.15:3128"},{"http":"115.46.64.105:8123"},{"http":"61.138.33.20:808"}]
    return ip_pool[num]

# 将json字典写入csv
def detectface(table_result, img, files_name):
    try:
        parsed = useapi(img)
        if not parsed['faces']:
            print('This picture do not have any face')
        else:
            if len(parsed['faces']) <= 5:  # face++免费版只能识别最多5张人脸
                parsed2 = parsed['faces']
            else:
                parsed2 = parsed['faces'][0:5]
            write_db(table_result, parsed2, files_name)
            print('The faces of this picture were gotten')
    except Exception as e:
        print(e)
        if ('parsed' in vars()):
            print(parsed['error_message'])
            if parsed['error_message'] == 'IMAGE_ERROR_UNSUPPORTED_FORMAT: image_file':
                print("图片有问题，跳过")
                return temp_data
        print('超过了并发数！等一下！')
        time.sleep(3)
        print('The program is going to work')
        detectface(img, temp_data, files_name)


def write_db(table_result, parsed2, files_name):
    for list_item in parsed2:
        temp = [0 for i in range(24)]  # 初始化一行，一共有24列
        # 写入文件名
        temp[0] = files_name

        # 写入时间戳
        daystamp, timestamp, hourstamp = gettimestamp(img)
        temp[1] = daystamp
        temp[2] = timestamp
        temp[3] = hourstamp

        # 写入api返回的数据
        emotion = [0 for i in range(7)]
        temp[4] = list_item["face_token"]
        temp[5] = list_item['attributes']['age']['value']
        temp[6] = list_item['attributes']['gender']['value']
        temp[7] = list_item['attributes']['ethnicity']['value']
        temp[8] = list_item['attributes']['emotion']['sadness']
        temp[9] = list_item['attributes']['emotion']['neutral']
        temp[10] = list_item['attributes']['emotion']['disgust']
        temp[11] = list_item['attributes']['emotion']['anger']
        temp[12] = list_item['attributes']['emotion']['surprise']
        temp[13] = list_item['attributes']['emotion']['fear']
        temp[14] = list_item['attributes']['emotion']['happiness']
        temp[15] = (temp.index(max(temp[8:15])))-8
        temp[16] = list_item['attributes']['smile']['threshold']
        temp[17] = list_item['attributes']['smile']['value']
        temp[18] = list_item['attributes']['beauty']['male_score']
        temp[19] = list_item['attributes']['beauty']['female_score']
        temp[20] = list_item['attributes']['skinstatus']['health']
        temp[21] = list_item['attributes']['skinstatus']['stain']
        temp[22] = list_item['attributes']['skinstatus']['acne']
        temp[23] = list_item['attributes']['skinstatus']['dark_circle']
        temp_row=tuple(temp)
        ins="INSERT INTO %s(PhotoName, daystamp, timestamp, hourstamp,faceID, age, gender, ethnicity, sadness,\
                 neutral,disgust, anger, surprise, fear, happiness, emotion,smile_threshold,smile_value,\
                 beauty_male,beauty_female,health,stain,acne,dark_circle) VALUES %s" %(table_result, str(temp_row))
        cursor.execute(ins)
        conn.commit()

    print('Success! The pic ' + str(files_name) + ' was detected!')


# 获取时间戳
def gettimestamp(img):
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

# 连接云mysql
def connectsql():
    try:
        conn=pymysql.connect(host = '172.27.0.11',  # 远程主机的ip地址，
                             user = 'root',   # MySQL用户名
                             db = 'emotion_part2',   # database名
                             passwd = 'hyj123456',   # 数据库密码
                             port = 3306,  #数据库监听端口，默认3306
                             charset = "utf8")  #指定utf8编码的连接
    except Exception as e:
        print(e)
    else:
        print('Connect success!')
        cursor = conn.cursor()
        return conn,cursor

if __name__ == '__main__':
    try:
        # 登录你的邮箱
        yag = yagmail.SMTP(user = 'your email', password = 'your password', host = 'smtp.qq.com')

        conn, cursor = connectsql()
        # 获取数据库中的表名
        cursor.execute("SELECT TABLE_NAME from information_schema.`TABLES` where TABLE_SCHEMA = 'emotion_part2'")
        table_list=cursor.fetchall()
        for table in table_list:
            table_name=table[0]
            if table_name =='machine10':
                continue
            print('Let us start dealing with table ' + table_name)

            table_result = table_name+'_result'

            # 判断表是否存在，存在的话就接着写，不存在的话，就要先创建一个表
            create_t=r'''
            CREATE TABLE IF NOT EXISTS %s (
                id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT UNIQUE,
                PhotoName TEXT,
                daystamp TEXT,
                timestamp TEXT,
                hourstamp DOUBLE,
                faceID TEXT,
                age TINYINT,
                gender TEXT,
                ethnicity TEXT,
                sadness DOUBLE,
                neutral DOUBLE,
                disgust DOUBLE,
                anger DOUBLE,
                surprise DOUBLE,
                fear DOUBLE,
                happiness DOUBLE,
                emotion TINYINT,
                smile_threshold TINYINT,
                smile_value DOUBLE,
                beauty_male DOUBLE,
                beauty_female DOUBLE,
                health DOUBLE,
                stain DOUBLE,
                acne DOUBLE,
                dark_circle DOUBLE
            )
            '''%table_result
            cursor.execute(create_t)

            # 遍历每个table里的图片
            cursor.execute("SELECT Count(*) FROM %s"%table_name)
            l = cursor.fetchall()[0][0]
            if table_name == 'machine11':
                s = 41
            else:
                s = 1
            for i in range(s,l+1):
                select_data=r"SELECT * FROM %s Where Id = %s"%(table_name ,str(i))
                cursor.execute(select_data)
                img_tuple = cursor.fetchall()

                img_name = img_tuple[0][1]
                img = img_tuple[0][2]
                print('Now, the program is going to deal with ' + table_name + ' pic' + img_name)

                detectface(table_result, img, img_name)
            # 发送邮件
            yag.send(to = ['924154233@qq.com'], subject = 'the table %s is done'%table_name, contents = ['table done!'])

        print('All done!')
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        # 要是报错了，就发邮件然后退出
        yag.send(to = ['接受邮箱'], subject = 'Break!!!!!', contents = [''])
        sys.exit(1)
