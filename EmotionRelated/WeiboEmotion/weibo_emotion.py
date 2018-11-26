# coding:utf-8
# version:python3.7
# author:Ivy

import json
import sqlite3
import time
import traceback
# 需要额外安装的包
import yagmail
import pandas
from PythonSDK.facepp import API


# 使用face++的api识别情绪
def useapi(url):
    try:
        parsed = api.detect(image_url=url, return_attributes="gender,age,emotion,beauty,smiling,ethnicity,skinstatus")
        return parsed
    except Exception as e:
        if e.code==403:
            if 'CONCURRENCY_LIMIT_EXCEEDED' in eval(e.body.decode())['error_message']:
                print('并发数超过限制')
                time.sleep(3)
                useapi(url)
        elif e.code==400:
            if 'IMAGE_FILE_TOO_LARGE' in eval(e.body.decode())['error_message']:
                print('图片太大，请更换')
                return 1
            elif 'INVALID_IMAGE_SIZE' in eval(e.body.decode())['error_message']:
                print('客户上传的图像像素尺寸太大或太小')
                return 1
            elif 'INVALID_IMAGE_URL' in eval(e.body.decode())['error_message']:
                print('图片URL错误或者无效')
                return 1
            elif 'IMAGE_ERROR_UNSUPPORTED_FORMAT' in eval(e.body.decode())['error_message']:
                print('图像无法正确解析，有可能不是一个图像文件、或有数据破损、或图片文件格式不符合要求')
                return 1
            else:
                print('error code:',e.code)
                print(e.body)
                return 2
        elif e.code==-1: # 在云主机运行不知道为什么会有error code = -1,但是值还是在的，所以才有这一块
            parsed=json.loads(e.body[27:-1])
            return parsed
        else:
            print('error code:',e.code)
            print(e.body)
            return 2

# 整理返回的信息
def detectface(row):
    url=row['img_large']
    parsed=useapi(url)
    if parsed == 1:
        url=row['img']
        parsed=useapi(url)
        if (parsed == 1) or (parsed == 2):
            print('图片无效，跳过')
            ins2="INSERT INTO pic_id VALUES (null, '%s')"%row['pid']
            cur1.execute(ins2)
            conn1.commit()
            return False
    elif parsed == 2:
        print('图片无效，跳过')
        ins2="INSERT INTO pic_id VALUES (null, '%s')"%row['pid']
        cur1.execute(ins2)
        conn1.commit()
        return False
    else:
        pass

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


def getinfo(row):
    pid=row['pid']
    sel='select weibo.time, weibo.created_time, weibo.place from weibo join pic join picweibo on weibo.weibo_id=picweibo.weibo_id and picweibo.pid=pic.pid where pic.pid="%s"'%pid
    cur2.execute(sel)
    info=cur2.fetchall()[0]
    place=info[2]

    # 处理时间
    t=info[0]
    ct=info[1]
    t_list=t.split('-')
    if ct[-3:] == '小时前':
        temp_h=int(t_list[3])-int(ct[:-3])
        if temp_h >= 0:
            h = temp_h
            d = int(t_list[2])
        else:
            h = 24-temp_h
            d = int(t_list[2])-1
        y = int(t_list[0])
        mon = int(t_list[1])
        min = int(t_list[4])
        s = int(t_list[5])
    elif ct[-3:] == '分钟前':
        # 分钟就忽略不计了
        y = int(t_list[0])
        mon = int(t_list[1])
        d = int(t_list[2])
        h = int(t_list[3])
        min = int(t_list[4])
        s = int(t_list[5])
    elif ct.count('-') == 1:
        # '11-10'这种格式的
        ct_list=ct.split('-')
        y = int(t_list[0])
        mon = int(ct_list[0])
        d = int(ct_list[1])
        h = int(t_list[3])
        min = int(t_list[4])
        s = int(t_list[5])
    elif ct.count('-') == 2:
        # '2014-12-11'这种格式的
        ct_list=ct.split('-')
        y = int(ct_list[0])
        mon = int(ct_list[1])
        d = int(ct_list[2])
        h = int(t_list[3])
        min = int(t_list[4])
        s = int(t_list[5])
    elif ct[:2] == '昨天':
        ct_list=ct.split(' ')
        ct_list=ct_list[1].split(':')
        y = int(t_list[0])
        mon = int(t_list[1])
        d = int(t_list[2])-1
        h = int(ct_list[0])
        min = int(ct_list[1])
        s = int(t_list[5])
    else:
        # 暂时还想不到有什么其他情况
        pass

    daystamp=str(y)+'-'+str(mon)+'-'+str(d)
    timestamp=str(h)+':'+str(min)+':'+str(s)
    hourstamp = h + min / 60.0 + s / 3600.0
    return place, daystamp, timestamp, hourstamp


def write_db(parsed2,row):
    for list_item in parsed2:
        # 写入文件名
        temp = [0 for i in range(25)]  # 初始化一行，一共有25列

        place, daystamp, timestamp, hourstamp = getinfo(row)
        # 写入文件名
        temp[0] = row['pid']

        # 写入时间戳
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
        temp[24] = place
        ins="INSERT INTO sample VALUES (null,"+",".join(["'%s'" %x for x in temp])+",null)"
        cur1.execute(ins)
        ins2="INSERT INTO pic_id VALUES (null, '%s')"%temp[0]
        cur1.execute(ins2)
        conn1.commit()


def createtable():
    create_t='''
    CREATE TABLE IF NOT EXISTS sample (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        pid TEXT,
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
        tag INTEGER
    )
    '''
    cur1.execute(create_t)
    create_t2='''
    CREATE TABLE IF NOT EXISTS pic_id (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        pid TEXT
    )
    '''
    cur1.execute(create_t2)
    conn1.commit()

def main():
    global conn1,cur1,conn2,cur2,api,yag
    # 创建使用facepp的实例
    API_KEY = 'TmBJ_UuRJyow1PWIjH6iIA3_25a_CIvp'
    API_SECRET = 'DndanQWy_q2ZIp7iMjMCSIkmdJU6V3Tl'

    api=API(API_KEY,API_SECRET)
    # 登录你的邮箱
    yag = yagmail.SMTP(user = '924154233@qq.com', password = 'atongmu100533', host = 'smtp.qq.com')


    # 连接数据库
    conn1 = sqlite3.connect('emotion.sqlite')
    cur1 = conn1.cursor()
    conn2 = sqlite3.connect('weibo.sqlite')
    cur2 = conn2.cursor()
    print('数据库连接成功!')

    # 初始化数据库
    createtable()

    # 获取所有待识别的照片的数量
    pic_pd = pandas.read_sql_query("SELECT * FROM pic",conn2) # 所有的照片信息
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

        temp_row=pic_pd_part.iloc[i]

        # 判断图片是否在数据库中
        pid = temp_row['pid']
        sel='select pid from sample where pid="%s"'%pid
        cur1.execute(sel)
        flag=cur1.fetchall()

        if len(flag)>0:
            print('这张图片识别过了！跳过！')
            continue

        # 判断图片格式
        if temp_row['img'][-3:] == 'gif':
            print('图片格式不对，跳过')
            continue

        detectface(temp_row)
        print('第%s张已经成功检测并写入'%str(i))

    print('目前所有的照片情绪都识别完了，休息三个小时再继续。')
    yag.send(to = ['924154233@qq.com'], subject = '情绪识别完毕', contents = ['目前所有的照片情绪都识别完了，休息三个小时再继续。'])

    # 关闭数据库
    cur1.close()
    cur2.close()
    conn1.close()
    conn2.close()
    print('数据库已关闭')


if __name__ == '__main__':
    while True:
        try:

            main()

            time.sleep(10800) # 休息三个小时
        except:
            e = traceback.format_exc()

            # 要是报错了，就发邮件然后退出
            print(e)
            yag.send(to = ['924154233@qq.com'], subject = '情绪识别 Break!!!!!', contents = [e])

            break
