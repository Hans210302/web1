from django.shortcuts import render,HttpResponse,redirect
import pymysql
import os
import redis
import random
import time
import json
import threading
from django.utils.timezone import now, timedelta
from qiniu import Auth
from urllib import parse
import hashlib
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.safestring import mark_safe



conn = pymysql.connect(host='localhost', user='root', passwd='970701', db='xunying', charset='utf8')  #连接数据库
cursor = conn.cursor(pymysql.cursors.DictCursor)
today = now().date() + timedelta(days=0)  # 今天
tomorrow = now().date() + timedelta(days=1)  # 明天
aftertomorrow = now().date() + timedelta(days=2)  # 后天
time=time.strftime('%H:%M',time.localtime(time.time())) #当前时间
lock = threading.Lock() #Lock对象

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

def index(request):
    if  request.method == "GET":
        # 查询正在热映电影
        lock.acquire()
        cursor.execute("select Movie_id,Movie_picture,Movie_date from Movie where Movie_date > DATE_SUB(curdate(), INTERVAL 30 DAY ) and  Movie_date<curdate() limit 8")
        lock.release()
        Movie_hot_list = cursor.fetchall()

        # 查询即将上映电影
        lock.acquire()
        cursor.execute("select Movie_id,Movie_picture,Movie_date from Movie where Movie_date>curdate() limit 8")
        lock.release()
        Movie_becoming_list = cursor.fetchall()

        # #查询票房
        lock.acquire()
        cursor.execute("select Movie.Movie_name,Movie.Movie_id,Movie.Movie_picture,Movie.Movie_type,Ticket.Ticket_score,Ticket.Ticket_id from Movie,Ticket where Movie.Movie_id=Ticket.Ticket_Movie_id   limit 1")
        lock.release()
        ticket_box_top = cursor.fetchone()

        lock.acquire()
        cursor.execute("select Movie.Movie_name,Movie.Movie_id,Movie.Movie_picture,Movie.Movie_type,Ticket.Ticket_score,Ticket.Ticket_id from Movie,Ticket where Movie.Movie_id=Ticket.Ticket_Movie_id   limit 1,9")
        lock.release()
        ticket_box_list = cursor.fetchall()

        # 查询最受期待电影
        lock.acquire()
        cursor.execute('select sum(Comment_like) as wantlook,Movie_id,Movie.Movie_name,Movie_type,Movie_date,Movie_picture   from Comment,Movie where Movie.Movie_id=Comment.Comment_Movie_id and Comment_look="想看" group by Comment_Movie_id order by wantlook desc limit 1;')
        lock.release()
        wantlook_Movie_top1= cursor.fetchone()
        cursor.execute('select sum(Comment_like) as wantlook,Movie_id,Movie.Movie_name  from Comment,Movie where Movie.Movie_id=Comment.Comment_Movie_id and Comment_look="想看" group by Comment_Movie_id order by wantlook desc limit 1,9;')
        wantlook_Movie_list = cursor.fetchall()
        return render(request,'index.html',{'Movie_hot_list':Movie_hot_list,'ticket_box_top':ticket_box_top,'Movie_becoming_list':Movie_becoming_list,'ticket_box_list':ticket_box_list,'wantlook_Movie_top1':wantlook_Movie_top1,'wantlook_Movie_list':wantlook_Movie_list})

#影院选座
@auth
def select_seat(request):
    if  request.method == "GET":
        Cfilm_id = request.GET.get('Cfilm_id')
        lock.acquire()
        cursor.execute("select Movie_name,Cfilm_date,Cfilm_time, Cfilm_price from Movie,Cinemafilm where Cinemafilm.cfilm_Movie_id=Movie.Movie_id and Cinemafilm.cfilm_id=%s" %Cfilm_id)
        lock.release()
        order_list= cursor.fetchone()
        return render(request,'select_seat.html',{"order_list":order_list,})
    else:
        name = request.POST.get('name')
        local = request.POST.get('local')
        number = request.POST.get('number')
        price = request.POST.get('price')
        nowdate = request.POST.get('nowdate')
        USERID =request.session.get('User_id')
        lock.acquire()
        cursor.execute('insert into Order (Order_Movie_name,Order_User_id,Order_local,Order_number,Order_price,Order_date) values (%s,%s,%s,%s,%s,%s)',[name,USERID,local,number,price,nowdate])
        lock.release()
        conn.commit()
        return render(request,'select_seat.html')


def login(request):
    if  request.method == "GET":
        return render(request, 'login.html')
    else:
        login_account = request.POST.get("login_account")
        login_pwd = request.POST.get("login_pwd")
        login_type = request.POST.get("login_type")
        if login_type == "1":
            lock.acquire()
            cursor.execute("select User_id,User_name from User where User_phone=%s and User_password=%s ",[login_account, login_pwd])
            lock.release()
            userinfo = cursor.fetchone()
            if userinfo == None:
                return HttpResponse("0")
            else:
                request.session["USERID"] = userinfo['User_id']
                request.session["USERNAME"] = userinfo['User_name']
                request.session["login_account"] = True
                return HttpResponse("1")
        elif login_type == "2":
            lock.acquire()
            cursor.execute("select Manage_id,Manage_name,Manage_Cinema_id from Manage where Manage_account=%s and Manage_password=%s ",[login_account, login_pwd])
            lock.release()
            manageinfo = cursor.fetchone()
            if manageinfo == None:
                return HttpResponse("0")
            else:
                request.session["MANAGEID"] = manageinfo['Manage_id']
                request.session["MANAGENAME"] = manageinfo['Manage_name']
                request.session["CINEMAID"] = manageinfo['Manage_Cinema_id']
                return HttpResponse("2")

def register(request):
    if  request.method == "GET":
        return render(request, 'register.html')
    else:
        nickname = request.POST.get("nickname")
        uphone = request.POST.get("uphone")
        password = request.POST.get("password")
        birth = request.POST.get("birth")
        sex = request.POST.get("sex")
        label = "-".join(request.POST.getlist("label[]"))
        cursor.execute("insert into User(User_name,User_password,User_sex,User_phone,User_birth,User_label) values(%s,%s,%s,%s,%s,%s) ",[nickname,password,sex,uphone,birth,label])
        conn.commit()
        return redirect('/myapp/login/')

# 判断手机号是否已注册
def check_phone(request):
    uphone = request.POST.get("phone1")
    cursor.execute('select * from User where User_phone=%s' %(uphone,))
    data_list = cursor.fetchone()
    if (data_list):
        return HttpResponse("1")
    else:
        return HttpResponse("0")

# 判断电影上线日期
def check_movie(request):
    Movie_id = request.POST.get('Movie_id')
    cursor.execute("select * from Movie where Movie_date > DATE_SUB(curdate(), INTERVAL 33 DAY ) and  Movie_date<curdate() and Movie_id=%s",[Movie_id,])
    Movie_info = cursor.fetchone()
    if Movie_info!=None:
        return HttpResponse("1")
    else:
        return HttpResponse("0")


# 电影详情
def movie_detail(request):
    if  request.method == "GET":
        session_id = request.session.get("USERID")
        Movie_id = request.GET.get("Movie_id")
        # 电影信息
        lock.acquire()
        cursor.execute("select * from Movie where Movie_id=%s", [Movie_id, ])
        lock.release()
        Movie_detail_list = cursor.fetchone()

        # 电影演员

        lock.acquire()
        cursor.execute("select * from Actor where Actor_Movie_id=%s", [Movie_id, ])
        lock.release()
        Movie_actor_list = cursor.fetchall()

        # 电影剧照
        lock.acquire()
        cursor.execute("select * from Moviepic where Moviepic_Movie_id=%s", [Movie_id, ])
        lock.release()
        Movie_pic_list = cursor.fetchall()

        # 电影热门评论
        lock.acquire()
        cursor.execute("select * from Comment where Comment_Movie_id=%s order by Comment_like desc limit 5", [Movie_id, ])
        lock.release()
        Movie_comment_list = cursor.fetchall()

        #电影最新评论
        lock.acquire()
        cursor.execute("select * from Comment where Comment_Movie_id=%s order by Comment_date desc limit 5", [Movie_id, ])
        lock.release()
        newMovie_comment_list = cursor.fetchall()
        lst={'Movie_detail_list': Movie_detail_list,'Movie_actor_list': Movie_actor_list,'Movie_pic_list': Movie_pic_list,'Movie_comment_list': Movie_comment_list,'newMovie_comment_list':newMovie_comment_list}

        if (session_id):
            lock.acquire()
            cursor.execute("insert into Active(active_user_id,active_movie_id,active_type,active_time) values(%s,%s,%s,%s)",[session_id,Movie_id,1,today])
            lock.release()
            conn.commit()
        return render(request, 'movie_detail.html',lst)
    else:
        return render(request, 'movie_detail.html')

# 电影页
def movie(request):
    if  request.method == "GET":
        # 查询正在热映电影
        cursor.execute("select Movie_id,Movie_picture,Movie_date from Movie where Movie_date > DATE_SUB(curdate(), INTERVAL 30 DAY ) and  Movie_date<curdate()")
        Movie_hot_list = cursor.fetchall()

        # 查询即将上映电影
        cursor.execute("select Movie_id,Movie_picture,Movie_date from Movie where Movie_date>curdate()")
        Movie_upcoming_list = cursor.fetchall()

        cursor.execute("select Movie_id,Movie_picture,Movie_date from Movie where Movie_date < DATE_SUB(curdate(), INTERVAL 30 DAY )")

        Movie_classic_list = cursor.fetchall()
        return render(request, 'movie.html',{'Movie_hot_list': Movie_hot_list,'Movie_upcoming_list': Movie_upcoming_list,'Movie_classic_list': Movie_classic_list})
    else:
        return render(request, 'movie.html')

def cinema(request):
    if  request.method == "GET":
        Cinema_id = request.GET.get("Cinema_id")
        cursor.execute("select * from Cinema where Cinema_id=%s", [Cinema_id, ])
        Cinema_list = cursor.fetchone()
        cursor.execute("select * from Movie where Movie_id=any(select distinct Cfilm_Movie_id from Cinemafilm where Cfilm_Cinema_id=%s) ", [Cinema_id, ])
        movive_list = cursor.fetchall()
        return render(request, 'cinema.html',{"Cinema_list":Cinema_list,"movive_list":movive_list})
    else:
        return render(request, 'cinema.html')

# 搜索结果
def searchresult(request):
    if  request.method == "GET":
        return render(request, 'searchresult.html')
    else:
        title = request.POST.get('search')
        title = '%' + title + '%'
        type="tab1"

        # 搜索演员
        cursor.execute("select * from Actor where Actor_name like '%s'" % title)
        actors = cursor.fetchall()
        if len(actors) != 0:
            type="tab3"

        # 搜索电影院
        cursor.execute("select * from Cinema where Cinema_name like '%s'" % title)
        Cinemas = cursor.fetchall()
        if len(Cinemas)!= 0:
            type="tab2"

        # 搜索电影
        cursor.execute("select * from Movie where Movie_name like '%s'" % title)
        Movies = cursor.fetchall()
        if len(Movies)!=0:
            type="tab1"
        return render(request, 'searchresult.html', {'Movies': Movies, 'Cinemas': Cinemas, 'actors': actors,'type': type, })


# 购票比较
def compare(request):
    if  request.method == "GET":
        Movie_id = request.GET.get("Movie_id")
        cursor.execute("select * from Cinema where Cinema_id=any(select distinct Cfilm_Cinema_id from Cinemafilm where Cfilm_Movie_id=%s)",[Movie_id,])
        Cinema_list = cursor.fetchall()
        cursor.execute('select * from Movie where Movie_id=%s',[Movie_id,])
        Movie_list = cursor.fetchone()
        return render(request, 'compare.html',{"Cinema_list":Cinema_list,"Movie_list":Movie_list,"Movie_id":Movie_id,})
    else:
        Movie_id = request.POST.get("movie_id")
        name1 = request.POST.get('name1')
        name2 = request.POST.get('name2')
        if name1 == '全部' and name2 == '全部':
            cursor.execute("select * from Cinema where Cinema_id=any(select distinct Cfilm_Cinema_id from Cinemafilm where Cfilm_Movie_id=%s)",[Movie_id,]);
            Movie_cinema_list = cursor.fetchall()
        elif name1 == '全部' and name2 != '全部':
            name2 = '%' + name2 + '%'
            cursor.execute("select distinct Cinema.Cinema_name,Cinema.Cinema_address,Cinema.Cinema_id,Cinema.Cinema_mao,Cinema.Cinema_tao,Cinema.Cinema_price,Cinema.lng,Cinema.lat from Cinema,Cinemafilm where Cfilm_Cinema_id=Cinema_id and Cfilm_Movie_id=%s and Cinema_address like '%s'" %(Movie_id,name2))
            Movie_cinema_list = cursor.fetchall()
        elif name2 == '全部' and name1 != '全部':
            name1 = '%' + name1 + '%'
            cursor.execute("select distinct Cinema.Cinema_name,Cinema.Cinema_address,Cinema.Cinema_id,Cinema.Cinema_mao,Cinema.Cinema_tao,Cinema.Cinema_price,Cinema.lng,Cinema.lat from Cinema,Cinemafilm where Cfilm_Cinema_id=Cinema_id and Cfilm_Movie_id=%s and Cinema_name like '%s'" %(Movie_id,name1))
            Movie_cinema_list = cursor.fetchall()
        else:
            name1 = '%' + name1 + '%'
            name2 = '%' + name2 + '%'
            cursor.execute("select distinct Cinema.Cinema_name,Cinema.Cinema_address,Cinema.Cinema_id,Cinema.Cinema_mao,Cinema.Cinema_tao,Cinema.Cinema_price,Cinema.lng,Cinema.lat from Cinema,Cinemafilm where Cfilm_Cinema_id=Cinema_id and Cfilm_Movie_id=%s and Cinema_address like '%s' and Cinema_name like '%s' " % (Movie_id,name2, name1))
            Movie_cinema_list = cursor.fetchall()
        list1 = ''
        for row in Movie_cinema_list:
            list = '''
                                 <tr>
                                     <td style="width: 1250px"><h4>''' + str(row["Cinema_name"]) + '''</h4>
                                         <p style="width: 850px"> ''' + str(row["Cinema_address"]) + ''' </p>
                                         <p>距我：<input type="text" class=''' + str(row['Cinema_id']) + ''' value="" style="border: 0;background-color: rgba(255,251,251,0)" disabled></p></td>
                                     <td><a href="/myapp/cinema/?Cinema_id=''' + str(row["Cinema_id"]) + '''"><input type="button" class="xunying_btn" value="寻影价：￥''' + str(row["Cinema_price"]) + ''' "></a>
                                         <p style="margin-left: 20px;font-size: 15px;">猫眼价：￥''' + str(row["Cinema_mao"]) + '''</p>
                                         <p style="margin-left: 20px;font-size: 15px;">淘宝价：￥''' + str(row["Cinema_tao"]) + '''</p>
                                     </td>
                                 </tr>
                                 <script>
                                   getPoint("''' + str(row["lng"]) + '''","''' + str(row["lat"]) + '''",".''' + str( row['Cinema_id']) + '''");
                                 </script>
                               
                             '''
            list1 = list1 + list
        return HttpResponse(list1)


# 返回订单详情
def order_detail(request):
    if  request.method == "GET":
        return render(request, 'order_detail.html')
    else:
        return render(request, 'order_detail.html')

# 订单详情
@auth
def book_detail(request):
    if  request.method == "GET":
        order_id = request.GET.get("Order_id")
        cursor.execute("select t_Order.Order_id,t_Order.Order_local,Cinemafilm.Cfilm_Movie_name,Cinemafilm.Cfilm_date,Cinemafilm.Cfilm_time,Cinema.Cinema_name,Cinema.Cinema_address,Cinema.Cinema_phone,Cinemafilm.Cfilm_price*t_Order.Order_number as toltal_price from t_Order,Cinemafilm,Cinema where t_Order.Order_Cfilm_id=Cinemafilm.Cfilm_id and Cinemafilm.Cfilm_Cinema_id=Cinema.Cinema_id and t_Order.Order_id=%s" %(order_id))
        row_list = cursor.fetchone()
        return render(request, 'book_detail.html',{'row_list':row_list})
    else:
        return render(request, 'personal_center.html')

#忘记密码
def password(request):
    if request.method == "POST":
        uphone = request.POST.get("uphone")
        password = request.POST.get("password")
        cursor.execute('Update User set User_password=%s where User_phone=%s'%(password,uphone))
        conn.commit()
        return render(request,'login.html')
    else:
        return render(request,'password.html')

# 评论
def comment(request):
    if  request.method == "GET":
        #最新影评
        cursor.execute('select * from User a,Longcomment b, Movie c where a.User_id=b.Longcomment_User_id and c.Movie_id=b.Longcomment_Movie_id order by Longcomment_date desc')
        longcommentnew=cursor.fetchall()
        #热门影评
        cursor.execute('select * from User a,Longcomment b, Movie c where a.User_id=b.Longcomment_User_id and c.Movie_id=b.Longcomment_Movie_id order by Longcomment_like desc')
        longcommenthot = cursor.fetchall()
        for row in longcommenthot:
            row['Longcomment_content']=mark_safe(row['Longcomment_content'])
        for row in longcommentnew:
            row['Longcomment_content']=mark_safe(row['Longcomment_content'])
        return render(request, 'comment.html',{'longcommentnew':longcommentnew,'longcommenthot':longcommenthot})
    else:
        return render(request, 'comment.html')

# 购票页面
def buyticket(request):
    if  request.method == "GET":
        Cinema_id = request.GET.get("Cinema_id")
        Movie_id = request.GET.get("Movie_id")
        # 查电影
        cursor.execute("select * from Movie where Movie_id=%s ",[Movie_id,])
        Movie_list = cursor.fetchone()
        # 查影院
        cursor.execute("select * from Cinema where Cinema_id=%s",[Cinema_id,])
        Cinema_list = cursor.fetchone()
        # 查场次
        cursor.execute("select * from Cinemafilm where Cfilm_Movie_id=%s and Cfilm_Cinema_id=%s and Cfilm_date=%s and Cfilm_time>%s", [Cinema_id,Movie_id,today,time ])
        Cinema_Movie_list = cursor.fetchall()
        return render(request, 'buyticket.html',{"Cinema_list":Cinema_list,"Movie_list":Movie_list,"Cinema_Movie_list":Cinema_Movie_list})
    else:
        return render(request, 'buyticket.html')

# 发送验证码
def note(request):
    # 放到redis，时间三分钟
    r = redis.Redis(host="47.100.43.197", port=6379, db=4, password=123456)
    a = random.randint(111111, 999999)
    data = request.POST['data1']
    r.set(data, a, 180)
    # 发送给手机
    from urllib import parse, request
    import json
    textmod = {"sid": "31026139ff358f4afe216f5fe861a469", "token": "553a4c28995214c874e46b7c87ec2e49",
               "appid": "3bbf9abda7884907aa313a67bb68c2cf", "templateid": "392344", "param": a,
               "mobile": data}
    textmod = json.dumps(textmod).encode(encoding='utf-8')
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                   "Content-Type": "application/json"}
    req = request.Request(url='https://open.ucpaas.com/ol/sms/sendsms', data=textmod, headers=header_dict)
    res = request.urlopen(req)
    res = res.read()
    num = request.POST.get('num')
    if (num == a):
        return HttpResponse("true")
    else:
        return HttpResponse('false')

# 获取今天影院上映电影
def buytoday(request):
    Cinema_id = request.POST.get("Cinema_id")
    Movie_id = request.POST.get("Movie_id")
    cursor.execute("select * from Cinemafilm where Cfilm_Movie_id=%s and Cfilm_Cinema_id=%s and Cfilm_date=%s and Cfilm_time>%s",
                   [Cinema_id, Movie_id, today,time])
    Cinema_Movie_list = cursor.fetchall()
    list1 = ''' 
    <table class="buyticket">
        <tr>
            <td>放映时间</td>
            <td>放映厅</td>
            <td>售价(元)</td>
            <td>选座购票</td>
        </tr>
     '''
    list2=''' '''
    for row in Cinema_Movie_list:
        list_temp = '''
            <tr>
                <td> ''' + str(row["Cfilm_time"]) + '''</td>
                <td> ''' + str(row["Cfilm_hall"]) + '''</td>  
                <td> ''' + str(row["Cfilm_price"]) + '''</td> 
                <td><a href="/myapp/select_seat/?Cfilm_id=''' + str(row["Cfilm_id"]) + '''"><input type="button" value="特惠购票" class="buy_btn"></a></td>
            </tr>
    '''
        list2=list2+list_temp
    list3 = '''</table> '''
    list = list1 + list2 + list3
    return HttpResponse(list)

# 获取明天影院上映电影
def buytomorrow(request):
    Cinema_id = request.POST.get("Cinema_id")
    Movie_id = request.POST.get("Movie_id")
    cursor.execute("select * from Cinemafilm where Cfilm_Movie_id=%s and Cfilm_Cinema_id=%s and Cfilm_date=%s",
                   [Cinema_id, Movie_id, tomorrow])
    Cinema_Movie_tomorrow = cursor.fetchall()
    list1 = ''' 
    <table class="buyticket">
        <tr>
            <td>放映时间</td>
            <td>放映厅</td>
            <td>售价(元)</td>
            <td>选座购票</td>
        </tr>
     '''
    list2=''' '''
    for row in Cinema_Movie_tomorrow:
        list_temp = '''
            <tr>
                <td> ''' + str(row["Cfilm_time"]) + '''</td>
                <td> ''' + str(row["Cfilm_hall"]) + '''</td>  
                <td> ''' + str(row["Cfilm_price"]) + '''</td> 
                <td><a href="/myapp/select_seat/?Cfilm_id=''' + str(row["Cfilm_id"]) + '''"><input type="button" value="特惠购票" class="buy_btn"></a></td>
            </tr>
    '''
        list2=list2+list_temp
    list3 = '''</table> '''
    list = list1 + list2 + list3
    return HttpResponse(list)

# 获取后天天影院上映电影
def buyaftertomorrow(request):
    Cinema_id = request.POST.get("Cinema_id")
    Movie_id = request.POST.get("Movie_id")
    cursor.execute("select * from Cinemafilm where Cfilm_Movie_id=%s and Cfilm_Cinema_id=%s and Cfilm_date=%s",
                   [Cinema_id, Movie_id,aftertomorrow])
    Cinema_Movie_aftertomorrow = cursor.fetchall()
    list1 = ''' 
    <table class="buyticket">
        <tr>
            <td>放映时间</td>
            <td>放映厅</td>
            <td>售价(元)</td>
            <td>选座购票</td>
        </tr>
     '''
    list2=''' '''
    for row in Cinema_Movie_aftertomorrow:
        list_temp = '''
            <tr>
                <td> ''' + str(row["Cfilm_time"]) + '''</td>
                <td> ''' + str(row["Cfilm_hall"]) + '''</td>  
                <td> ''' + str(row["Cfilm_price"]) + '''</td> 
                <td><a href="/myapp/select_seat/?Cfilm_id=''' + str(row["Cfilm_id"]) + '''"><input type="button" value="特惠购票" class="buy_btn"></a></td>
            </tr>
    '''
        list2=list2+list_temp
    list3 = '''</table> '''
    list = list1 + list2 + list3
    return HttpResponse(list)


def getseat(request):
    Cfilm_id = request.POST.get("Cfilm_id")
    cursor.execute("select Cfilm_local from Cinemafilm  where Cfilm_id=%s",[Cfilm_id,])
    local_list = cursor.fetchone()
    try:
        local=local_list["Cfilm_local"]
        seat_list=list(local.split("#"))
        return HttpResponse(json.dumps({'seat_list': seat_list}, ensure_ascii=False))
    except Exception:
        return HttpResponse({'seat_list': local_list})


def getprice(request):
    Cfilm_id = request.POST.get("Cfilm_id")
    cursor.execute("select Cfilm_price from Cinemafilm  where Cfilm_id=%s",[Cfilm_id,])
    price= cursor.fetchone()
    pri=int(price["Cfilm_price"])
    return HttpResponse(pri)

@auth
def insertseat(request):
    Cfilm_id = request.POST.get("Cfilm_id")
    sql_local = request.POST.get("sql_local")
    cursor.execute("update Cinemafilm  set Cfilm_local=CONCAT(Cfilm_local,%s) where Cfilm_id=%s; ",[sql_local,Cfilm_id])
    conn.commit()
    return HttpResponse("ok")

@auth
def write(request):
    Movie_id = request.GET.get("Movie_id")
    cursor.execute('select * from Movie where Movie_id=%s',[Movie_id, ])
    Movie_list = cursor.fetchall()
    return render(request, 'writecomment.html', {"Movie_list": Movie_list})

#写影评
@auth
def wcomment(request):
    content=request.POST['m2']
    id1=request.POST.get('movie_id')
    session_id = request.session.get('USERID')
    if (session_id):
        cursor.execute("insert into Active(active_user_id,active_movie_id,active_type,active_time) values(%s,%s,%s,%s)",
                       [session_id, id1, 4, today])
    now_time="{} {}".format(today,time)
    title=request.POST.get('title')
    cursor.execute("insert into Longcomment(Longcomment_Movie_id,Longcomment_User_id,Longcomment_content,Longcomment_date,Longcomment_like,Longcomment_nolike,Longcomment_title)values(%s,%s,%s,%s,%s,%s,%s)",[id1,session_id,content,now_time,'0','0',title])
    conn.commit()
    return redirect("/myapp/movie_detail/?Movie_id="+str(id1))


def openpic(request):
    from qiniu import Auth, put_file, etag
    import qiniu.config
    from PIL import Image
    from aip import AipImageCensor
    a=request.FILES.get("imageData")#得到图片
    b=random.randint(111111,999999)
    key='s2'+str(b)+'.jpg'
    Image=Image.open(a)
    Image.save('s1.jpg')#保存本地
    APP_ID = '10027473'
    API_KEY = 'vuVlmlKsXULFfo438jiWfxb0'
    SECRET_KEY = '33Iew8K4zT3hBBI1YqGPaK9vcHD5dAxG'
    client = AipImageCensor(APP_ID, API_KEY, SECRET_KEY)
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()
    img = get_file_content('s1.jpg')
    result = client.imageCensorUserDefined(img)
    if result['conclusion']=='合规':
    # path = default_storage.save('s1.jpg', ContentFile(Image.read()))

        access_key = 'EjIqvG2iluFxOx-PzeIyCNUKqUL2je9Q5bfunOyg'
        secret_key = 'pqt97zqOt7cw07a9AWwEXPp0zofB_9swvTVJGOOr'
        q = Auth(access_key, secret_key)
        bucket_name = 'xunyingpicture'
        localfile = r"s1.jpg"
        token = q.upload_token(bucket_name, key)
        ret,info = put_file(token, key, localfile)
        #返回图片地址
        return HttpResponse('http://files.g8.xmgc360.com/'+key)
    else:
        return HttpResponse("1")



@auth
def addOrder(request):
    Cfilm_id = request.POST.get("Cfilm_id")
    cursor.execute("select Cfilm_Movie_id from Cinemafilm where Cfilm_id=%s",[Cfilm_id])
    movie_id = cursor.fetchone()
    sql_local = request.POST.get("sql_local")
    user_id = request.session.get('USERID') #用户id
    if (user_id):
        cursor.execute("insert into Active(active_user_id,active_movie_id,active_type,active_time) values(%s,%s,%s,%s)",
                       [user_id, movie_id['Cfilm_Movie_id'], 5, today])
    Order_time=str(today)+' '+str(time)
    number=len(sql_local.split("#"))-1
    cursor.execute("insert into t_Order(Order_user_id, Order_local, Order_date,Order_number, Order_Cfilm_id)  values(%s,%s,%s,%s,%s)",[user_id,sql_local,Order_time,number,Cfilm_id])
    t_Order_id = int(cursor.lastrowid)
    conn.commit()
    cursor.execute("select * from t_Order,Cinemafilm,Cinema where t_Order.Order_Cfilm_id=Cinemafilm.Cfilm_id and Cinemafilm.Cfilm_Movie_id=Cinema.Cinema_id  and Order_id=%s",[t_Order_id,])
    Order_info = cursor.fetchone()
    return HttpResponse(json.dumps({'Order_info': Order_info}, ensure_ascii=False))

def long_comment_add(request):
    long_Comment_id = request.POST.get("long_Comment_id")
    Comment_like = request.POST.get("Comment_like")
    cursor.execute("update Longcomment set Longcomment_like=%s where Longcomment_id=%s ",[Comment_like,long_Comment_id])
    conn.commit()
    return HttpResponse("ok!")

def long_comment_sub(request):
    long_Comment_id = request.POST.get("long_Comment_id")
    Comment_nolike = request.POST.get("Comment_nolike")
    cursor.execute("update Longcomment set Longcomment_like=%s where Longcomment_id=%s ",[Comment_nolike,long_Comment_id])
    conn.commit()
    return HttpResponse("ok!")