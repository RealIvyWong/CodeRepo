# -*- coding: utf-8 -*-
# version:python3.6.6
# author:Ivy Wong

# 本循环是对一个大文件夹内的多个小文件夹中的图片进行识别，每个小文件夹为一个csv文件
# 也就是说有两级文件夹目录
# 注意，路径与文件名都不要有中文

# 导入相关模块
import time, os
import sqlite3
import json
import traceback
import urllib.request
import urllib.error
# 需要额外安装的库
import pandas
import yagmail

http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'

key = 'TmBJ_UuRJyow1PWIjH6iIA3_25a_CIvp'
secret = 'DndanQWy_q2ZIp7iMjMCSIkmdJU6V3Tl'


# 使用face++的api识别情绪
def useapi(img):


    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
    data.append(key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
    data.append(secret)
    data.append('--%s' % boundary)

    data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(img)

    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
    data.append('1')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
    data.append("gender,age,emotion,beauty,smiling,ethnicity,skinstatus")
    data.append('--%s--\r\n' % boundary)

    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')

    http_body = b'\r\n'.join(x for x in data)
    #http_body = b'\r\n'.join(data)

    # build http request
    req = urllib.request.Request(url=http_url, data=http_body)

    # header
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

    try:
        # post data to server
        resp = urllib.request.urlopen(req, timeout=5)
        # get response
        qrcont = resp.read()
        # if you want to load as json, you should decode first,
        # for example: json.loads(qrount.decode('utf-8'))
        parsed = json.loads(qrcont.decode('utf-8'))
        return parsed
    except urllib.error.HTTPError as e:
        print(e.read().decode('utf-8'))

def detectface(row):
    pid=row['pid']
    sel='select Data from pic where pid="%s"'%pid
    cur2.execute(sel)
    img=cur2.fetchall()[0][0]
    parsed = useapi(img)

    # 如果图片有问题的话
    if (parsed == 1) or (parsed == 2):
        print('图片无效，跳过')
        ins2="INSERT INTO pic_id VALUES (null, '%s')"%row['pid']
        cur1.execute(ins2)
        conn1.commit()
        return False

    # 如果图片没有脸的话
    if not parsed['faces']:
        print('This picture do not have any face')
        ins2="INSERT INTO pic_id VALUES (null, '%s')"%row['pid']
        cur1.execute(ins2)
        conn1.commit()
        return False

    if len(parsed['faces']) <= 5:  # face++免费版只能识别最多5张人脸
        parsed2 = parsed['faces']
    else:
        parsed2 = parsed['faces'][0:5]
    write_db(parsed2,row)
    return True

def write_db(parsed2,row):
    for list_item in parsed2:
        # 写入文件名
        temp = [0 for i in range(26)]  # 初始化一行，一共有24列
        # 写入文件名
        temp[0] = row['PhotoName']

        # 写入时间戳
        temp[1] = row['daystamp']
        temp[2] = row['timestamp']
        temp[3] = row['hourstamp']

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
        temp[24] = row['place']
        temp[25] = row['pid']
        ins="INSERT INTO sample VALUES (null,"+",".join(["'%s'" %x for x in temp])+",null)"
        cur1.execute(ins)
        ins2="INSERT INTO pic_id VALUES (null, '%s')"%row['pid']
        cur1.execute(ins2)
        conn1.commit()


def createtable():
    create_t='''
    CREATE TABLE IF NOT EXISTS sample (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        PhotoName TEXT,
        daystamp TEXT,
        timestamp TEXT,
        hourstamp REAL,
        faceID TEXT,
        age INTEGER,
        gender TEXT,
        ethnicity TEXT,
        sadness REAL,
        neutral REAL,
        disgust REAL,
        anger REAL,
        surprise REAL,
        fear REAL,
        happiness REAL,
        emotion INTEGER,
        smile_threshold INTEGER,
        smile_value REAL,
        beauty_male REAL,
        beauty_female REAL,
        health REAL,
        stain REAL,
        acne REAL,
        dark_circle REAL,
        place TEXT,
        pid TEXT,
        tag INTEGER
    )
    '''
    cur1.execute(create_t)
    create_t2='''
    CREATE TABLE IF NOT EXISTS pic_id (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        pid INTEGER
    )
    '''
    cur1.execute(create_t2)
    conn1.commit()

def main():
    global conn1,cur1,conn2,cur2,yag

    # 登录你的邮箱
    yag = yagmail.SMTP(user = '924154233@qq.com', password = 'atongmu100533', host = 'smtp.qq.com')

    # 连接数据库
    conn1 = sqlite3.connect('emotion.sqlite')
    cur1 = conn1.cursor()
    conn2 = sqlite3.connect('photo.sqlite')
    cur2 = conn2.cursor()
    print('数据库连接成功!')

    # 初始化数据库
    createtable()

    # 获取所有待识别的照片的数量
    pic_pd = pandas.read_sql_query("SELECT pid FROM pic",conn2) # 所有的照片信息
    emotion_pd = pandas.read_sql_query("SELECT * FROM pic_id",conn1) #已经识别了的照片信息
    pid_al = list(pic_pd['pid'].values) # 所有的照片编码
    pid_rl = list(emotion_pd['pid'].values) # 已经识别了的照片编码
    pid_nl = list(set(pid_al)-set(pid_rl)) # 待识别的照片编码
    pic_pd_part = pic_pd[pic_pd.pid.isin(pid_nl)] # 待识别的照片信息
    n = pic_pd_part.shape[0]
    print('全部有{}张照片，已经识别了{}张，还剩{}张'.format(len(pid_al), len(pid_rl), len(pid_nl)))

    print('************************准备识别%s张图片************************'%str(n))
    for i in range(n):
        print('正在准备识别第%s张图片'%str(i+1))

        # 判断图片是否已经在数据库中
        pid=pic_pd_part.iloc[i,0]
        sel='select pid from sample where pid="%s"'%pid
        cur1.execute(sel)
        flag=cur1.fetchall()

        if len(flag)>0:
            print('这张图片识别过了！跳过！')
            continue

        # 获取当前数据行
        sel='select PhotoName, daystamp, timestamp, hourstamp, place, pid from pic where pid="%s"'%pid
        temp_row=pandas.read_sql_query(sel,conn2).iloc[0,:]

        detectface(temp_row)

        print('第%s张已经成功检测并写入'%str(i))

    print('所有的照片情绪都识别完了!')
    yag.send(to = ['924154233@qq.com'], subject = '情绪识别完毕', contents = ['本地所有的照片情绪都识别完了。'])

    # 关闭数据库
    cur1.close()
    conn1.close()
    cur2.close()
    conn2.close()

if __name__ == '__main__':
    try:
        main()
    except:
        e = traceback.format_exc()

        # 要是报错了，就发邮件然后退出
        print(e)
        yag.send(to = ['924154233@qq.com'], subject = '本地情绪识别 Break!!!!!', contents = [e])
