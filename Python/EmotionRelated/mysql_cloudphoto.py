# -*- coding: utf-8 -*-
# version:python3.7.0
# author:Ivy Wong

import pymysql
import sys
import os.path

# 用来将本地图片上传到云数据库中
# 还不成熟，以后再来改


# 连接云数据库
def connectsql():
    try:
        conn=pymysql.connect(host = 'cdb-77ldfnig.cd.tencentcdb.com',  # 远程主机的ip地址，
                             user = 'root',   # MySQL用户名
                             db = 'emotion_part2',   # database名
                             passwd = 'hyj123456',   # 数据库密码
                             port = 10014,  #数据库监听端口，默认3306
                             charset = "utf8")  #指定utf8编码的连接
    except Exception as e:
        print(e)
        sys.exit(1)
    else:
        print('Connect success!')
        cursor = conn.cursor()
        return conn,cursor

def uploadimg(folder,filename,photo):
    try:
        add_row=r"INSERT INTO "+folder+r"(Name,Data) VALUES(%s,%s)"
        cursor.execute(add_row, (filename,photo)) # 可能会报错1300，是因为微博数据缺少相片的timestamp的信息
        conn.commit()
    except pymysql.Error as e:
        print(e)
        sys.exit(1)

def createtable(folder):
    drop_table =r"DROP TABLE IF EXISTS %s"%folder
    cursor.execute(drop_table) # 可能会报错1501，不存在这个表，但是没关系
    create_table=r'''CREATE TABLE %s(Id INT(11) PRIMARY KEY AUTO_INCREMENT,
                                    Name VARCHAR(30),
                                    Data LONGBLOB NOT NULL)'''%folder
    cursor.execute(create_table)
    conn.commit()

if  __name__ == '__main__':
    conn, cursor = connectsql()
    path = "D:/EmotionRawData/test2" # 第一级目录
    for root, dirs, files in os.walk(path, topdown=False):
        for folder in dirs:
            print('Let us start dealing with folder ' + folder)
            createtable(folder)

            # 遍历每个folder里的图片
            for root2, dirs2, files2 in os.walk(path + '/' + folder):
                for files_name in files2:
                    img = path + '/' + folder + '/' + files_name
                    print('Now, the program is going to upload ' + folder + ' pic ' + str(files_name))
                    f = open(img,'rb')
                    photo = f.read()
                    uploadimg(folder,files_name,photo)
                    f.close()
                    print('Folder %s pic %s was uploaded.'%(folder, str(files_name)))
            print('The folder %s is done.'%folder)

    print('All done!')
    cursor.close()
    conn.close()
