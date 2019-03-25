# coding:utf-8
# version:python3.7
# author:Ivy

############# 程序功能 ####################
#    本程序用来获取百度地图某城市某种poi周围一定范围内的另一种类型的poi数据
#    如示例是获取武汉市中学周围500米内的网吧
#    生成的info.txt格式如下
#     1, xxx中学
#     1-1， xxx网吧
#     1-2， xxx网吧
#     2， xxx中学
#     2-1, xxx网吧
############################################

import requests,json
import time,sys

############### 自主设置区 ###############
ak = '8AgtU92Xa9ZQIDYcex3tTeGzHtOpN3On' #API key
keyword="中学"
keyword2="网吧"
radius=500
city="武汉市"
baseBound = '29.972898,113.707695,31.367052,115.085775' #武汉市矩形框的左下角经纬度和右上角经纬度
############################################


# 构造header
headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'Accept-Encoding':'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Host': 'api.map.baidu.com',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'DNT': '1'
}

baseUrl="http://api.map.baidu.com/place/v2/search?query={}&bounds={}&page_size=20&page_num={}&output=json&ak={}"
searchBaseUrl="http://api.map.baidu.com/place/v2/search?query={}&location={}&radius={}&output=json&ak={}&page_size=20&page_num={}"

def req(url):
    # 访问url获取返回的数据读取为json
    errorNum=0
    while True:
        try:
            res = requests.get(url,headers=headers)
            res.encoding='utf-8'
            jd = json.loads(res.text)
            return jd
        except Exception as e:
            errorNum+=1
            print("出错了！")
            print(e)
            if errorNum==5:
                sys.exit(1)
            time.sleep(1)

def splitArea(bound):
    # 分割矩形区域的函数
    boundList=[]
    row_num = 2 # 按照 2 X 2 进行分割
    bound=list(map(float,bound.split(',')))
    step_lat = (bound[2] - bound[0]) / row_num
    step_lon = (bound[3] - bound[1]) / row_num
    for i in range(0,row_num):
        for j in range(0,row_num):
            boundTemp = []
            boundTemp.append(bound[0]+step_lat*i)
            boundTemp.append(bound[1]+step_lon*j)
            boundTemp.append(bound[0]+step_lat*(i+1))
            boundTemp.append(bound[1]+step_lon*(j+1))
            boundTemp=",".join(["%s" %x for x in boundTemp])
            # 是否要继续分割
            if check(boundTemp):
                boundList.append(boundTemp)
            else:
                boundList+=splitArea(boundTemp)
    return boundList

def check(bound):
    # 检查一下当前矩形框是否需要再次分割
    checkUrl=baseUrl.format(keyword,bound,0,ak)
    checkJd=req(checkUrl)
    if checkJd["total"]<400:
        return True
    return False

def getPois(bound):
    # 获取一定范围内所有的想要的poi的信息
    poiListTemp=[]
    pageNum=0
    while True:
        getUrl=baseUrl.format(keyword,bound,pageNum,ak)
        getJd=req(getUrl)
        if getJd['results']==[]: # 如果这一页没数据了就是结束啦，退出循环
            break
        for result in getJd['results']:
            if result["city"] != city: # 在矩形框中，但是不是想要的城市的，就不要记录啦
                continue
            poiListTemp.append(result)
        pageNum+=1
    print("当前区域{}的poi已爬完，共有{}个".format(bound,len(poiListTemp)))
    return poiListTemp

def searchPois(poiInfo):
    # 获取某个poi周边的其他poi信息
    poiListTemp=[]
    pageNum=0
    while True:
        searchUrl=searchBaseUrl.format(keyword2,str(poiInfo['location']['lat'])+','+str(poiInfo['location']['lng']),radius,ak,pageNum)
        searchJd=req(searchUrl)
        if searchJd['results']==[]:
            break
        for result in searchJd['results']:
            poiListTemp.append(result["name"])
            print(result["name"]," 已添加")
        pageNum+=1
    print(poiInfo["name"],"周边poi已爬完")
    return [poiInfo["name"],poiListTemp]

if __name__ == '__main__':
    # 分割想要的区域
    boundList=splitArea(baseBound)
    print(boundList)

    # 获取范围内所有的poi信息
    poiList=[]
    for bound in boundList:
        poiList+=getPois(bound)
    print('已获得所有poi信息')

    # 对于获取到的每个poi进行周边检索
    infoList=[]
    for poi in poiList:
        infoList.append(searchPois(poi))
    print('已获得所有周边poi信息')

    # 把获取到的信息都写入txt
    with open('info.txt','w') as f:
        for i in range(len(infoList)):
            f.write(str(i+1)+', '+infoList[i][0]+'\n')
            for j in range(len(infoList[i][1])):
                f.write(str(i+1)+'-'+str(j+1)+', '+infoList[i][1][j]+'\n')
    print("所获得的信息已全部写入txt啦！")
