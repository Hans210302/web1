from django.shortcuts import render, HttpResponse, redirect
import pymysql
import os
import redis
import random
import threading
import json,wave
from aip import AipSpeech
import time
from django.utils.timezone import now, timedelta
from django.utils.safestring import mark_safe
today = now().date() + timedelta(days=0)  # 今天
Time=time.strftime('%H:%M',time.localtime(time.time())) #当前时间
lock = threading.Lock() #Lock对象
conn = pymysql.connect(host='localhost', user='root', passwd='970701', db='xunying', charset='utf8')  # 连接数据库
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 登陆验证
def auth(func):
 # 判断是否登录装饰器
    def inner(request, *args, **kwargs):
        ok = request.session.get("USERID")
        # 如果没有登陆返回到login.html
        if ok==None:
            return redirect("/myapp/login/")
        return func(request, *args, **kwargs)
    return inner


# 写短评
# @auth
def review(request):
    import urllib
    movie_name = request.POST['movie']
    session_name = request.session.get('USERNAME')
    session_id=request.session.get('USERID')
    id1 = request.POST['movie1']
    if (session_id):
        cursor.execute("insert into Active(active_user_id,active_movie_id,active_type,active_time) values(%s,%s,%s,%s)",
                       [session_id, id1, 2, today])
        look = request.POST['choice']
        star = request.POST['star']
        content1 = request.POST['content']
        date = now().date() + timedelta(days=0)
        now_time="{0} {1}".format(date,Time)
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=kT8o0IxopsPwp8dswWCV54ww&client_secret=8jPrgXlKj7c2mvDtkeqcTQe83RhdKLzV'
        formate = {"content": content1}
        data = urllib.parse.urlencode(formate).encode('utf-8')
        request = urllib.request.Request(host)
        request.add_header('Content-Type', 'application/json; charset=UTF-8')
        response = urllib.request.urlopen(request)
        content = response.read()
        if (content):
            content = eval(content.decode("utf8"))["access_token"]
            host1 = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam?access_token=' + content
            request = urllib.request.Request(host1, data)
            request.add_header('Content-Type', 'application/json; charset=UTF-8')
            response = urllib.request.urlopen(request)
            content = response.read()
            content = eval(content.decode("utf8"))
            result = content['result']
            if result['spam']==0:
                cursor.execute("insert into Comment(Comment_Movie_id,Movie_name,User_name,comment_content,Comment_date,Comment_star,Comment_like,Comment_look,Comment_User_id)values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [id1, movie_name, session_name, content1, now_time, star, '0', look,session_id])
                conn.commit()
                # return redirect("/myapp/movie_detail/?Movie_id=" + str(id1)+"&check=no")
                return HttpResponse("0")
            else:
                # return redirect("/myapp/movie_detail/?Movie_id=" + str(id1)+"&check=yes")
                return HttpResponse("1")  #存在敏感词
    else:
        print(5)
        return HttpResponse("2")

#点赞
def zan(request):
    num = request.POST['num']
    comment_id = request.POST['commid']
    cursor.execute("update Comment set Comment_like=%s where Comment_id=%s", [num, comment_id])
    conn.commit()
    cursor.execute("select * from Comment ")
    list = cursor.fetchall()
    list1 = ''''''
    for row in list:
        list2 = '''
        <div>
            <h3>
                <span>
                    <a>''' + str(row['User_name']) + '''</a>
                    <span>''' + str(row['Comment_look']) + '''</span>
                    <span></span>
                    <span>''' + str(row['Comment_date']) + ''' </span>
                    </span>
                    <span class="praise">
                        <span class="praise1"><img src="../../static/image/zan.png" class="praise-img"/></span>
                                <span class="praise-txt">''' + str(row['Comment_like']) + '''</span>
                                <span class="add-num" style="display: none"><em>+1</em></span>
                                <input type="text" value="''' + str(row['Comment_id']) + '''" style="display: none"
                                       class="commid">
                            </span>
                        </h3>
                        <p>
                            ''' + str(row['Comment_content']) + '''
                        </p>
                        <hr>
                    </div>'''
        list1 = list1 + list2
    return HttpResponse(list1)


# 影评评论
def reply(request):
    long_id = request.GET.get('Longcomment_id')
    cursor.execute("select * from User a,Longcomment b, Movie c where a.User_id=b.Longcomment_User_id and c.Movie_id=b.Longcomment_Movie_id and b.Longcomment_id=%s" % (long_id))
    longcommenthot = cursor.fetchall()
    cursor.execute("select * from Reply a,User b where a.Reply_User_id=b.User_id and a.Reply_Longcomment_id=%s" % (long_id))
    replylist = cursor.fetchall()
    for row in longcommenthot:
        row['Longcomment_content'] = mark_safe(row['Longcomment_content'])
    return render(request, 'reply.html', {'longcommenthot': longcommenthot, 'replylist': replylist})


# 点击评论
@auth
def make(request):
    long_id = request.POST['h7']
    content = request.POST['h6']
    User_id = request.session.get('USERID')
    date = now().date() + timedelta(days=0)
    now_time="{} {}".format(date,Time)
    cursor.execute("insert into Reply(Reply_Longcomment_id,Reply_date,Reply_User_id,Reply_content)values (%s,%s,%s,%s)",
                   [long_id, now_time, User_id, content])
    conn.commit()
    cursor.execute(
        "select * from Reply a,User b where a.Reply_User_id=b.User_id and a.Reply_Longcomment_id=%s" % (long_id))
    replylist = cursor.fetchall()
    list = ''' '''
    for row in replylist:
        list1 = '''
        <div class="comment" user="self">
                <div class="comment-right">
                    <div class="comment-text"><span class="user">''' + str(row['User_name']) + '''：</span>''' + str(
            row['Reply_content']) + '''</div>
                    <div class="comment-date">''' + str(row['Reply_date']) + '''
                    </div>
                </div>
            </div>'''
        list = list + list1
    return HttpResponse(list)


def totle(request):
    lg_id = request.POST['lg']
    totle = request.POST['totle']
    totle = int(totle) + 1
    cursor.execute("update Longcomment set Longcomment_like=%s where Longcomment_id=%s", [totle, lg_id])
    conn.commit()
    cursor.execute("select Longcomment_like from Longcomment where Longcomment_id=%s", [lg_id])
    like = cursor.fetchall()
    return HttpResponse(like[0]['Longcomment_like'])


def new(request):
    mid = request.POST['mid']
    cursor.execute("select * from Comment where Comment_Movie_id=%s order by Comment_date desc limit 5", [mid,])
    newMovie_comment_list = cursor.fetchall()
    list = ''''''
    for row in newMovie_comment_list:
        if str(row['Comment_star'])=='1':
            li='''<span class="start123">
                    <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li><li></li><li></li><li></li></ul></span>'''
        if str(row['Comment_star'])=='2':
            li='''<span class="start123">
                    <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li><li></li><li></li></ul></span>'''
        if str(row['Comment_star'])=='3':
            li='''<span class="start123">
                    <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li ><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li><li></li></ul></span>'''
        if str(row['Comment_star'])=='4':
            li='''<span class="start123">
                    <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li ><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li></ul></span>'''
        if str(row['Comment_star'])=='5':
            li='''<span class="start123">
                    <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li ><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li></ul></span>'''
        list1 = ''' <div>
                            <span>
                                <span style="color:#37a">''' + str(row['User_name']) + '''</span>
                                <span style="font-size: 15px">
                                <span>''' + str(row['Comment_look']) + '''</span>
                                <span></span>
                                <span>''' + str(row['Comment_date']) + '''</span>'''+li+'''
                                </span>
                            </span>
                            <h3>
                            <span class="praise">
                                <span class="praise1"><img src="../../static/image/zan.png" class="praise-img"/></span>
                                <span class="praise-txt">''' + str(row['Comment_like']) + '''</span>
                                <span class="add-num" style="display: none"><em>+1</em></span>
                                <input type="text" value="''' + str(row['Comment_id']) + '''" style="display: none"
                                       class="commid">
                            </span>
                            </h3>
                        <p>
                            ''' + str(row['Comment_content']) + '''
                        </p>
                        <hr>
                    </div>'''
        list = list + list1
    return HttpResponse(list)

def hoot(request):
    mid = request.POST['mid']
    lock.acquire()
    cursor.execute("select * from Comment where Comment_Movie_id=%s order by Comment_like desc limit 5", [mid, ])
    newMovie_comment_list = cursor.fetchall()
    lock.release()
    list = ''''''
    for row in newMovie_comment_list:
        if str(row['Comment_star']) == '1':
            li = '''<span class="start123">
                      <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li><li></li><li></li><li></li></ul></span>'''
        if str(row['Comment_star']) == '2':
            li = '''<span class="start123">
                      <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li><li></li><li></li></ul></span>'''
        if str(row['Comment_star']) == '3':
            li = '''<span class="start123">
                      <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li ><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li><li></li></ul></span>'''
        if str(row['Comment_star']) == '4':
            li = '''<span class="start123">
                      <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li ><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li></li></ul></span>'''
        if str(row['Comment_star']) == '5':
            li = '''<span class="start123">
                      <ul><li style="background: url('../../static/image/starsy.png')no-repeat"></li ><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li><li style="background: url('../../static/image/starsy.png')no-repeat"></li></ul></span>'''
        list1 = ''' <div>
                        
                            <span>
                                <span style="color:#37a">''' + str(row['User_name']) + '''</span>
                                <span style="font-size: 15px">
                                <span>''' + str(row['Comment_look']) + '''</span>
                                <span></span>
                                <span>''' + str(row['Comment_date']) + '''</span>'''+li+'''
                                </span>
                            </span>
                            <h3>
                            <span class="praise">
                                <span class="praise1"><img src="../../static/image/zan.png" class="praise-img"/></span>
                                <span class="praise-txt">''' + str(row['Comment_like']) + '''</span>
                                <span class="add-num" style="display: none"><em>+1</em></span>
                                <input type="text" value="''' + str(row['Comment_id']) + '''" style="display: none"
                                       class="commid">
                            </span>
                        </h3>
                        <p>
                            ''' + str(row['Comment_content']) + '''
                        </p>
                        <hr>
                    </div>'''
        list = list + list1
    return HttpResponse(list)

def save_wave_file(filename, data):
    framerate = 8000
    NUM_SAMPLES = 2000
    channels = 1
    sampwidth = 1
    TIME = 2
    '''save the date to the wavfile'''
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()



def ceshi1(request):
    a = request.FILES.get('audioData')
    save_wave_file('hp.pcm', a)
    APP_ID = '14732392'
    API_KEY = 'zuTYrPRVgPuFgOsZ2vdKrSDY'
    SECRET_KEY = 'g20Ldy5F32jjQwo3arBWQX9Tj5GgU9Pk'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
    rtn = client.asr(get_file_content('hp.pcm'), 'pcm', 8000, {
        'dev_pid': 1536,})
    return HttpResponse(rtn['result'][0])

def yuying(request):
    a = request.FILES.get('audioData')
    save_wave_file('hp.pcm', a)
    APP_ID = '14732392'
    API_KEY = 'zuTYrPRVgPuFgOsZ2vdKrSDY'
    SECRET_KEY = 'g20Ldy5F32jjQwo3arBWQX9Tj5GgU9Pk'
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
    rtn = client.asr(get_file_content('hp.pcm'), 'pcm', 8000, {
        'dev_pid': 1536, })
    print(rtn)
    if 'result' in rtn:
        if '登录' in rtn['result'][0]:
            return HttpResponse('/myapp/login/')
        elif '注册' in rtn['result'][0]:
            return HttpResponse('/myapp/register/')
        elif '影院' in rtn['result'][0]:
            return HttpResponse('/myapp/cinema_new/')
        elif '电影' in rtn['result'][0]:
            return HttpResponse('/myapp/movie/')
        elif '影评' in rtn['result'][0]:
            return HttpResponse( '/myapp/comment/')
        elif '注销' in rtn['result'][0]:
            return HttpResponse( '/myapp/logout/')
        elif '退出' in rtn['result'][0]:
            return HttpResponse( '/myapp/logout/')
        elif '宝贝' in rtn['result'][0]:
            return HttpResponse('/myapp/movie_detail/?Movie_id=1/')
        elif '战士' in rtn['result'][0]:
            return HttpResponse('/myapp/movie_detail/?Movie_id=28/')
        else:
            return HttpResponse(1)
    else:
        return HttpResponse(1)


def page404(request):
    return render(request,'404.html')

