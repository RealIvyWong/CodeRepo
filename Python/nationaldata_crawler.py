# coding:utf-8
# version:python3.7
# author:Ivy

# 本脚本用来爬取国家数据的近十年的年度数据
# 根据指标树构建文件夹树进行存储
# 需要提供自己的账号密码在设置区内设置
# 因为是使用的selenium进行爬取，稳定是稳定，就是慢!

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import os,shutil

def create_folder(lastpath,name):
    path=lastpath+'\\'+name
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def child_index(father,father_id):
    if len(father.find_elements_by_id(father_id+'_ul'))>0:
        tags=father.find_element_by_id(father_id+'_ul').find_elements_by_tag_name('li')
        #print('这个指标【{}】是有子指标的'.format(father.find_element_by_id(father_id+'_span').text))
        return tags
    #print('这个指标【{}】没有子指标'.format(father.find_element_by_id(father_id+'_span').text))
    return False

def dowork(tag,path):
    now_id=tag.get_attribute('id')
    print('开始处理这个指标【{}】'.format(tag.find_element_by_id(now_id+'_span').text))
    # 把要点击的拖动滚动条到视野范围内
    driver.execute_script("arguments[0].scrollIntoView();", tag.find_element_by_id(now_id+'_span'))
    # 点击一下span这个标签
    tag.find_element_by_id(now_id+'_span').click()

    if child_index(tag,now_id):
        sub_tags=child_index(tag,now_id)
        sub_path=create_folder(path,tag.find_element_by_id(now_id+'_span').text)
        # 过滤一些已经下载了的
        fl=os.listdir(sub_path)
        fn=0
        for f in fl:
            if os.path.isfile(sub_path+'\\'+f):
                fn+=1
        if fn!=len(sub_tags):
            for sub_tag in sub_tags:
                dowork(sub_tag,sub_path)
    else:
        oldname=dir+'\\'+'年度数据.xls'
        name=tag.find_element_by_id(now_id+'_span').text
        newname=path+'\\'+name+'.xls'

        if not os.path.exists(newname):# 判断是不是下载过的
            # 把要点击的拖动滚动条到视野范围内
            driver.execute_script("arguments[0].scrollIntoView();", driver.find_element_by_xpath('//*[@id="site"]/div[2]/ul[2]/li[1]/a'))
            # 没有子指标的话，就点下载
            driver.find_element_by_xpath('//*[@id="site"]/div[2]/ul[2]/li[1]/a').click()
            # 等待弹出下载框
            WebDriverWait(driver,3).until(EC.visibility_of_element_located((By.CSS_SELECTOR,"[class='doneDodnload btn']")))

            # 点击下载
            driver.find_element_by_css_selector("[class='doneDodnload btn']").click()
            # 修改文件名
            while not os.path.exists(oldname):
                time.sleep(3)
            print(newname,'已经保存好了文件')
            shutil.move(oldname,newname)

if __name__ == '__main__':
    #设置区
    dir='C:\\Users\\Ivy\\Downloads' #保存的目录
    #账号密码
    email=None
    password=None

    # 模拟登陆
    driver = webdriver.Chrome()
    driver.get('http://data.stats.gov.cn/login.htm')
    driver.maximize_window()
    yzm=input('输入验证码：')
    driver.find_element_by_xpath('//*[@id="username"]').send_keys(email)
    driver.find_element_by_xpath('//*[@id="keyp"]').send_keys(password)
    driver.find_element_by_xpath('//*[@id="verifyCode"]').send_keys(yzm)
    driver.find_element_by_xpath('//*[@id="auto_login"]').click()
    driver.find_element_by_name("submitBtn").click()
    driver.implicitly_wait(10)
    driver.switch_to_window(driver.window_handles[-1])
    driver.get('http://data.stats.gov.cn/easyquery.htm?cn=C01')

    # 获取第一级指标
    index_c1=driver.find_element_by_id('treeZhiBiao_1')
    id_c1=index_c1.get_attribute('id')

    index_c2_l=child_index(driver,id_c1)
    path_1=create_folder(dir,index_c1.find_element_by_id(id_c1+'_span').text)

    for i in range(12,len(index_c2_l)):
        index_c2=index_c2_l[i]
        dowork(index_c2,path_1)

    print('done')
