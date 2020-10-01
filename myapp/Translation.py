from django.shortcuts import render,HttpResponse,redirect
import pymysql
import time
import random
from random import choice
import json
from urllib.request import urlopen, quote
import requests


conn = pymysql.connect(host='localhost', user='root', passwd='970701', db='xunying', charset='utf8')  #连接数据库
cursor = conn.cursor(pymysql.cursors.DictCursor)


#地址转换为经纬度
# cursor.execute("select Cinema_address from Cinema ")
# address_list = cursor.fetchall()
# print(address_list[0])
# i=1
# for row in address_list:
#     url = 'http://api.map.baidu.com/geocoder/v2/'
#     output = 'json'
#     ak = 'DnnSjGqWORfbnkZMZ2oLgN7wBGxPSgFw' # 浏览器端密钥
#     address = quote(row['Cinema_address']) # 由于本文地址变量为中文，为防止乱码，先用quote进行编码
#     uri = url + '?' + 'address=' + address  + '&output=' + output + '&ak=' + ak
#     req = urlopen(uri)
#     res = req.read().decode()
#     temp = json.loads(res)
#     lat = temp['result']['location']['lat']
#     lng = temp['result']['location']['lng']
#     print(lat,lng)
#     cursor.execute("Update Cinema set lat=%s,lng=%s where Cinema_id=%s",(lat,lng,i))
#     i=i+1
# conn.commit()

#随机时间
# a1=(2018,1,1,0,0,0,0,0,0)              #设置开始日期时间元组
# a2=(2018,11,8,23,59,59,0,0,0)    #设置结束日期时间元组
# start=time.mktime(a1)    #生成开始时间戳
# end=time.mktime(a2)      #生成结束时间戳
# for i in range(1,1000):
    # t=random.randint(start,end)    #在开始和结束时间戳中随机取出一个
    # date_touple=time.localtime(t)          #将时间戳生成时间元组
    # date=time.strftime("%Y-%m-%d",date_touple)  #将时间元组转成格式化字符串

#计算时间差
# from datetime import datetime,timedelta
# a1='2018-10-07'
# a2='2017-10-05'
# test1=datetime.strptime(a1, "%Y-%m-%d")
# test2=datetime.strptime(a2, "%Y-%m-%d")
# diff=test1-test2
# print(diff.days)


#个人推荐数据生成
# foo= ['1','1,2','1,4','1,5','1,2,4','1,2,5','1,4,5','1,2,4,5']
# for i in range(10000):
#     type = choice(foo)
#     user=random.randint(33,1030)
#     movie=random.randint(1,110)
#     year=random.randint(2017,2018)
#     month=random.randint(1,11)
#     date=random.randint(1,29)
#     time=str(year)+'-'+str(month)+'-'+str(date)
#     score=random.randint(1,5)
#     if movie ==23:
#         movie=random.randint(24,110)
#     cursor.execute("insert into Active(active_user_id,active_movie_id,active_type,active_time)values (%s,%s,%s,%s)",[user,movie,type,time])
#     conn.commit()
#     print(user,movie,type,time)

score={'爱情':4,'喜剧':5,'动作':3,'悬疑':3,'战争':2,'冒险':2,'科幻':3,'犯罪':3,'动画':2,'剧情':3,'古装':3,'恐怖':1}
title=['爱情','喜剧','动作','悬疑','战争','冒险','科幻','犯罪','动画','剧情','古装','恐怖']
#用户倾向性
def suggestion(data_list):
    import datetime
    import numpy as np
    import pandas as pd
    today=datetime.datetime.today()
    use,use_1=[],[]
    for row in data_list:
        from datetime import datetime, timedelta
        title_1 = title.copy()
        time = datetime.strptime(row["active_time"],"%Y-%m-%d")
        weight = list(map(int, row["active_type"].split(',')))
        type = list(row["Movie_type"].split(' / '))
        diff=(today-time).days
        if diff > 360:
            utility1=0
        else:
            utility= (8.049 + -0.012*(diff) - 0.0001*(diff)*(diff) + 2.605*(10**-7)*(diff)*(diff)*(diff))/10
            utility1 = round(utility,3)
        for j in range(len(title_1)):
            if title_1[j] in type:
                title_1[j] = round(score[title_1[j]]*sum(weight)*utility1,3)
            else:
                title_1[j] = 0
        use_1.append(title_1)
    df = pd.DataFrame(use_1)
    for m in df.columns:
        use.append(df[m].sum())
    return use

def  CosSimilarity(p1,p2):
    import math
    s = sum([p1[item]* p2[item] for item in range(len(p1))])
    den1 = math.sqrt(sum([pow(p1[item],2) for item in range(len(p1))]))
    den2 = math.sqrt(sum([pow(p2[item],2) for item in range(len(p2))]))
    if den2==0:
        return 0
    else:
        return s/(den1*den2)


def suggest_login(request):
    session_id = request.session.get('USERID')
    cursor.execute("select Movie.Movie_type,Active.active_type,Active.active_time from Movie,Active where Active.active_movie_id=Movie.Movie_id and Active.active_user_id=%s",[session_id])
    data_list = cursor.fetchall()
    movie_similar = []
    if (data_list):
        user_beh = suggestion(data_list)
        cursor.execute("select Movie_type,Movie_id from Movie")
        type_list = cursor.fetchall()
        for row in type_list:
            title_1 = title.copy()
            type = list(row["Movie_type"].split(' / '))
            for j in range(len(title_1)):
                if title_1[j] in type:
                    title_1[j] = score[title_1[j]]
                else:
                    title_1[j] = 0
            similay = CosSimilarity(user_beh,title_1)
            if similay>0.75:
                movie_similar.append(row["Movie_id"])
        print(movie_similar)
    else:
        cursor.execute("select User_label from User where User_id=%s",[session_id,])
        label = cursor.fetchall()
        cursor.execute("select Movie_type,Movie_id from Movie")
        type_list = cursor.fetchall()
        use_type = list(label.split('_'))
        if len(use_type)>3:
            for row in type_list:
                movie_type = list(row["Movie_type"].split(' / '))
                if set(use_type)>= set(movie_type):
                    movie_similar.append(row["Movie_id"])
        elif len(use_type)>0:
            for row in type_list:
                movie_type = list(row["Movie_type"].split(' / '))
                if set(use_type)>= set(movie_type):
                    movie_similar.append(row["Movie_id"])
                else:
                    movie_similar.append(row["Movie_id"])
        else:
            type =['爱情','喜剧','动作','古装','冒险','科幻']
            for row in type_list:
                movie_type = list(row["Movie_type"].split(' / '))
                if set(type)>= set(movie_type):
                    movie_similar.append(row["Movie_id"])
    

# def suggest_unlogin(request):
#     cursor.execute("select Movie_type,Movie_id from Movie")
#     type_list = cursor.fetchall()
#     type = ['爱情', '喜剧', '动作', '古装', '冒险', '科幻']
#     movie_similar = []
#     for row in type_list:
#         movie_type = list(row["Movie_type"].split(' / '))
#         if set(type) >= set(movie_type):
#             movie_similar.append(row["Movie_id"])
#     print(movie_similar)












