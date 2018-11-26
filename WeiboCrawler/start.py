# coding:utf-8
# version:python3.7
# author:Ivy

import crawler
import buildip
import time
import yagmail
import pandas


if __name__ == '__main__':
    emailname='924154233@qq.com'
    emailpassword='atongmu100533'
    # 登录你的邮箱
    yag = yagmail.SMTP(user = emailname, password = emailpassword, host = 'smtp.qq.com')

    # 位置个数
    temp_pd = pandas.read_csv("pid.csv")
    n=temp_pd.shape[0]

    while True:



        time_start=time.time()

        # 建立代理池
        ippool=buildip.buildippool()
        #ippool=[{}] # 测试专用行

        print('*************************开始爬取%s个地点的微博*********************'%str(n))
        #建立进程
        for i in range(n):
            crawler.main(i,ippool)

        time_end=time.time()
        print(' time cost ',time_end-time_start,'s')

        print('***********************休息三小时再继续爬********************')
        yag.send(to = ['924154233@qq.com'], subject = 'All Done', contents = ['这一段时间的都爬完了，三个小时后继续。耗时%s秒'%str(time_end-time_start)])
        time.sleep(10800) #设置3个小时执行一次
