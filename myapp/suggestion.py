from django.shortcuts import render,HttpResponse,redirect
import pymysql
import time
import json
import random
from random import choice


conn = pymysql.connect(host='localhost', user='root', passwd='970701', db='xunying', charset='utf8')  #连接数据库
cursor = conn.cursor(pymysql.cursors.DictCursor)


score = {'爱情': 4, '喜剧': 5, '动作': 3, '悬疑': 3, '战争': 2, '冒险': 2, '科幻': 3, '犯罪': 3, '动画': 2, '剧情': 3, '古装': 3, '恐怖': 1}
title = ['爱情', '喜剧', '动作', '悬疑', '战争', '冒险', '科幻', '犯罪', '动画', '剧情', '古装', '恐怖']

# 基于用户行为协同过滤，求相似用户
def suggestion(data_list):
    import datetime
    import numpy as np
    import pandas as pd
    today = datetime.datetime.today()
    use, use_1 = [], []
    for row in data_list:
        from datetime import datetime, timedelta
        title_1 = title.copy()
        time = datetime.strptime(row["active_time"], "%Y-%m-%d")
        weight = list(map(int, row["active_type"].split(',')))
        type = list(row["Movie_type"].split(' / '))
        diff = (today - time).days
        if diff > 360:
            utility1 = 0
        else:
            utility = (8.049 + -0.012 * (diff) - 0.0001 * (diff) * (diff) + 2.605 * (10 ** -7) * (diff) * (diff) * (
                diff)) / 10   #时间效用函数
            utility1 = round(utility, 3)
        for j in range(len(title_1)):
            if title_1[j] in type:
                title_1[j] = round(score[title_1[j]] * sum(weight) * utility1, 3)
            else:
                title_1[j] = 0
        use_1.append(title_1)
    df = pd.DataFrame(use_1)
    for m in df.columns:
        use.append(df[m].sum())
    return use

#余弦算法求相似度
def CosSimilarity(p1, p2):
    import math
    s = sum([p1[item] * p2[item] for item in range(len(p1))])
    den1 = math.sqrt(sum([pow(p1[item], 2) for item in range(len(p1))]))
    den2 = math.sqrt(sum([pow(p2[item], 2) for item in range(len(p2))]))
    if den2 == 0:
        return 0
    else:
        return s / (den1 * den2)


def suggest(request):
    session_id = request.session.get('USERID')
    if (session_id):
        cursor.execute("select Movie.Movie_type,Active.active_type,Active.active_time from Movie,Active where Active.active_movie_id=Movie.Movie_id and Active.active_user_id=%s",[session_id])
        data_list = cursor.fetchall()
        movie_similar = {}
        if (data_list):
            user_beh = suggestion(data_list)
            cursor.execute("select Movie_type,Movie_id from Movie")
            type_list = cursor.fetchall()
            for row in type_list:
                title_1 = title.copy()
                type = row["Movie_type"].split(' / ')
                for j in range(len(title_1)):
                    if title_1[j] in type:
                        title_1[j] = score[title_1[j]]
                    else:
                        title_1[j] = 0
                similay = CosSimilarity(user_beh, title_1)
                if similay > 0.5:
                    movie_similar[row["Movie_id"]] = similay
            movie_similar = sorted(movie_similar.items(), key=lambda x: x[1], reverse=True)
        else:
            cursor.execute("select User_label from User where User_id=%s", [session_id, ])
            label = cursor.fetchone()
            cursor.execute("select Movie_type,Movie_id from Movie")
            type_list = cursor.fetchall()
            use_type = label['User_label'].split('-')
            if len(use_type) > 0:
                title_2 = title.copy()
                for j in range(len(title_2)):
                    if title_2[j] in use_type:
                        title_2[j] = score[title_2[j]]
                    else:
                        title_2[j] = 0
                for row in type_list:
                    title_1 = title.copy()
                    movie_type = row["Movie_type"].split(' / ')
                    for j in range(len(title_1)):
                        if title_1[j] in movie_type:
                            title_1[j] = score[title_1[j]]
                        else:
                            title_1[j] = 0
                    similay = CosSimilarity(title_2, title_1)
                    if similay > 0.5:
                        movie_similar[row["Movie_id"]] = similay
                movie_similar = sorted(movie_similar.items(), key=lambda x: x[1], reverse=True)
            else:
                type = ['爱情', '喜剧', '动作', '古装', '冒险', '科幻']
                for row in type_list:
                    movie_type = row["Movie_type"].split(' / ')
                    if set(type) >= set(movie_type):
                        movie_similar[row["Movie_id"]] = "ok"
        cursor.execute("select Comment_Movie_id from Comment where Comment_look='看过' and Comment_User_id=%s",[session_id])
        watch_list = cursor.fetchall()
        data_list=[]
        for data in movie_similar:
            if data[0] in watch_list:
                continue
            else:
                cursor.execute("select * from Movie where Movie_id=%s",[data[0],])
                data_list1 = cursor.fetchone()
                data_list.append(data_list1)
        list1 = ''
        for row in data_list[:12]:
            list = '''
                <div class="suggest_movie">
                    <a href="/myapp/movie_detail/?Movie_id=''' + str(row["Movie_id"]) + '''"><img src="''' + str(row["Movie_picture"]) + '''" class="shadow"  style="height:197px;width:145px;"></a>
                    <a href="/myapp/movie_detail/?Movie_id=''' + str(row["Movie_id"]) + '''"><input type="button" class="shadow" value="情有独钟" ></a>
                </div>    
                    '''
            list1 = list1 + list
        return HttpResponse(list1)

    else:
        cursor.execute("select Movie_type,Movie_id from Movie")
        type_list = cursor.fetchall()
        type = ['爱情', '喜剧', '动作', '古装', '冒险', '科幻']
        movie_similar = []
        for row in type_list:
            movie_type = row["Movie_type"].split(' / ')
            if set(type) >= set(movie_type):
                movie_similar.append(row["Movie_id"])
        data_list=[]
        for data in movie_similar:
            cursor.execute("select * from Movie where Movie_id=%s",[data,])
            data_list1 = cursor.fetchone()
            data_list.append(data_list1)
        list1 = ''
        for row in data_list[:12]:
            list = '''
                <div class="suggest_movie">
                    <a href="/myapp/movie_detail/?Movie_id=''' + str(row["Movie_id"]) + '''"><img src="''' + str(row["Movie_picture"]) + '''" class="shadow" style="height:197px;width:145px;"></a>
                    <a href="/myapp/movie_detail/?Movie_id=''' + str(row["Movie_id"]) + '''"><input type="button" class="shadow"  value="情有独钟" ></a>
                </div>     
                    '''
            list1 = list1 + list
        return HttpResponse(list1)


#基于商品的推荐
def movie_suggest(request):
    movie_id = request.POST.get("Movie_id")
    cursor.execute("select Movie_type from Movie where Movie_id=%s",[movie_id])
    data = cursor.fetchone()
    data_list = data['Movie_type'].split(' / ')
    title_2 = title.copy()
    for j in range(len(title_2)):
        if title_2[j] in data_list:
            title_2[j] = score[title_2[j]]
        else:
            title_2[j] = 0
    movie_similar = {}
    if (data_list):
        cursor.execute("select Movie_type,Movie_id from Movie where Movie_id not in (%s)",[movie_id])
        type_list = cursor.fetchall()
        for row in type_list:
            title_1 = title.copy()
            type = row["Movie_type"].split(' / ')
            for j in range(len(title_1)):
                if title_1[j] in type:
                    title_1[j] = score[title_1[j]]
                else:
                    title_1[j] = 0
            similay = CosSimilarity(title_2, title_1)
            if similay > 0.5:
                movie_similar[row["Movie_id"]] = similay
        movie_similar1 = sorted(movie_similar.items(), key=lambda x: x[1], reverse=True)
        data_list1 = []
        for line in movie_similar1[:6]:
            cursor.execute("select * from Movie where Movie_id=%s",[line[0]])
            data1 = cursor.fetchone()
            data_list1.append(data1)
        list1 = ''
        for row in data_list1:
            list = '''
                 <div class="movie_pic" style="float: left;margin-right:20px;width:130px">
                        <a href="/myapp/movie_detail/?Movie_id=''' + str(row["Movie_id"]) + '''"><img src="''' + str(row["Movie_picture"]) + '''" style="height:180px;width:130px;"></a>
                        <br>
                        <span style="text-align:center;">''' + str(row["Movie_name"]) + '''</span>
                 </div>    
                    '''
            list1 = list1 + list
        return HttpResponse(list1)