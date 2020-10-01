from django.shortcuts import render,HttpResponse,redirect
import pymysql
import json
from myapp.pay import AliPay
import threading

conn = pymysql.connect(host='localhost', user='root', passwd='970701', db='xunying', charset='utf8')  #连接数据库
cursor = conn.cursor(pymysql.cursors.DictCursor)
lock = threading.Lock() #Lock对象

# 登陆验证
def auth_manage(func):
 # 判断是否登录装饰器
    def inner(request, *args, **kwargs):
        ok = request.session.get("MANAGEID")
        # 如果没有登陆返回到login.html
        if ok==None:
            return redirect("/myapp/login/")
        return func(request, *args, **kwargs)
    return inner

@auth_manage
def manager(request):
    if  request.method == "GET":
        return render(request, 'manager_nav.html')
    else:
        return render(request, 'manager_nav.html')


# 场次管理
@auth_manage
def field_manage(request):
    # if  request.method == "GET":
        # Cinema_id = request.GET.get("Cinema_id")
        # 查场次
        Cinema_id = request.session.get('CINEMAID')
        cursor.execute("select * from Cinemafilm,Movie where Cinemafilm.Cfilm_Movie_id=Movie.Movie_id and Cfilm_Cinema_id=%s ",[Cinema_id,])
        Movie_list = cursor.fetchall()
        return render(request, 'field_manage.html',{"Movie_list": Movie_list, })
    # else:
    #     return render(request, 'field_manage.html')

# 编辑场次
@auth_manage
def edit_field(request):
    if  request.method == "GET":
        Cfilm_id = request.GET.get("Cfilm_id")
        cursor.execute("select * from Cinemafilm where Cfilm_id=%s ",[Cfilm_id,])
        Movie_info_list = cursor.fetchone()
        return render(request, 'edit_field.html',{"Movie_info_list": Movie_info_list, })
    else:
        try:
            Cfilm_id = request.GET.get("Cfilm_id")
            date = request.POST.get('date')
            time = request.POST.get('time')
            hall = request.POST.get('hall')
            price = request.POST.get('price')
            cursor.execute("update Cinemafilm set Cfilm_date = %s ,Cfilm_time = %s ,Cfilm_hall = %s ,Cfilm_price = %s where Cfilm_id = %s",[date,time,hall,price,Cfilm_id])
            conn.commit()
            return HttpResponse("1")
        except Exception:
            return HttpResponse("0")


# 删除场次
@auth_manage
def delete_field(request):
    if request.session.get('USERID') == None:
        if  request.method == "GET":
            Cfilm_id = request.GET.get("Cfilm_id")
            cursor.execute("delete  from Cinemafilm where Cfilm_id=%s ",[Cfilm_id,])
            conn.commit()
            return redirect("/myapp/field_manage/")
        else:
            return render(request, 'field_manage.html')

#电影管理
@auth_manage
def movie_manage(request):
    if  request.method == "GET":
        Cinema_id = request.session.get('CINEMAID')
        cursor.execute("select * from Movie where Movie_id=any(select CM_Movie_id from Cinema_Movie_manage where CM_Cinema_id=%s ) and Movie_date > DATE_SUB(curdate(), INTERVAL 30 DAY )",[Cinema_id,])
        Movie_list = cursor.fetchall()
        return render(request,'movie_manage.html',{"Movie_list": Movie_list, })
    else:
        return render(request, 'movie_manage.html')

# 电影下线
@auth_manage
def outline(request):
    Cinema_id = request.session.get('CINEMAID')
    Movie_id = request.POST.get("Movie_id")
    try:
        cursor.execute('delete from Cinema_Movie_manage where CM_Movie_id=%s and CM_Cinema_id=%s',[Movie_id,Cinema_id])
        return HttpResponse("1")
    except:
        return HttpResponse("0")

# 电影下线判断
def outlinejudge(request):
    Movie_id = request.POST.get("Movie_id")
    Cinema_id = request.session.get('CINEMAID')
    cursor.execute(" select *  from Cinemafilm where Cfilm_Movie_id=%s and Cfilm_Cinema_id=%s",[Movie_id,Cinema_id])
    Movie_list = cursor.fetchone()
    if Movie_list !=None:
        return HttpResponse("1")
    else:
        return HttpResponse("0")


# 电影上线
@auth_manage
def online(request):
    if  request.method == "GET":
        Cinema_id = request.session.get('CINEMAID')
        cursor.execute("select * from Movie where Movie_date > DATE_SUB(curdate(), INTERVAL 30 DAY )")
        Movie_all_list = cursor.fetchall()
        return render(request,'online.html',{"Movie_all_list": Movie_all_list, })
    else:
        return render(request, 'online.html')

# 选择电影上线
@auth_manage
def chonline(request):
    Cinema_id = request.session.get('CINEMAID')
    Movie_id = request.POST.get("Movie_id")
    cursor.execute(" select *  from Cinema_Movie_manage where CM_Movie_id=%s and CM_Cinema_id=%s",[Movie_id,Cinema_id])
    Movie_list = cursor.fetchone()
    if Movie_list !=None:
        return HttpResponse("1")
    else:
        cursor.execute('insert into Cinema_Movie_manage (CM_Movie_id,CM_Cinema_id) values (%s,%s)',[Movie_id,Cinema_id])
        conn.commit()
        return HttpResponse("0")


# 影院管理
@auth_manage
def cinema_manage(request):
    if  request.method == "GET":
        return render(request,'cinema_manage.html')
    else:
        return render(request, 'cinema_manage.html')

# 增加场次
@auth_manage
def add_field(request):
    if  request.method == "POST":
        try:
            Movie_id = request.POST.get("Movie_id")
            Cinema_id = request.session.get('CINEMAID')
            date = request.POST.get("date")
            time = request.POST.get("time")
            hall = request.POST.get("hall")
            price = request.POST.get("price")
            cursor.execute('insert into Cinemafilm (Cfilm_Movie_id,Cfilm_Cinema_id,Cfilm_hall,Cfilm_date,Cfilm_time,Cfilm_price) values (%s,%s,%s,%s,%s,%s)',[Movie_id,Cinema_id,hall,date,time,price])
            conn.commit()
            return HttpResponse("1")
        except:
            return HttpResponse("1")


# 影院管理
@auth_manage
def cinema_manage(request):
    if  request.method == "GET":
        Cinema_id = request.session.get('CINEMAID')
        cursor.execute("select * from Cinema where Cinema_id=%s ",[Cinema_id,])
        Cinema_info_list = cursor.fetchone()
        return render(request, 'cinema_manage.html',{"Cinema_info_list": Cinema_info_list, })
    else:
        Cinema_id = request.GET.get("Cinema_id")
        Cinema_name = request.POST.get('cinema_name')
        Cinema_address = request.POST.get('cinema_address')
        Cinema_phone = request.POST.get('cinema_phone')
        cursor.execute("update Cinema set Cinema_name = %s ,Cinema_address = %s ,Cinema_phone = %s where Cinema_id = %s",[Cinema_name,Cinema_address,Cinema_phone,Cinema_id])
        conn.commit()
        return redirect('/myapp/field_manage/')

@auth_manage
def order_manage(request):
    Cinema_id = request.session.get('CINEMAID')
    cursor.execute("select Order_id,Movie_name,Order_user_id,Order_local,concat(Cinemafilm.Cfilm_date,' ',Cinemafilm.Cfilm_time) as Cfilm_watchtime,Order_number,Cfilm_price,Order_date,Order_number*Cfilm_price as total_price from t_Order,Cinemafilm,Movie where Cinemafilm.Cfilm_id=t_Order.Order_Cfilm_id and Cinemafilm.Cfilm_Movie_id=Movie.Movie_id and Cfilm_Cinema_id=%s",[Cinema_id, ])
    order_info_list = cursor.fetchall()
    return render(request, 'order_manage.html',{"order_info_list":order_info_list})

# 查看选座情况
@auth_manage
def seat_manage(request):
    if  request.method == "GET":
        return render(request,'seat_manage.html')
    else:
        return render(request, 'seat_manage.html')

def judge_status(request):
    if  request.method == "POST":
        Order_id = request.POST.get("Order_id")
        lock.acquire()
        cursor.execute("select * from t_Order,Cinemafilm where Order_Cfilm_id=Cfilm_id and concat(Cinemafilm.Cfilm_date,' ',Cinemafilm.Cfilm_time)>now() and Order_id=%s",[Order_id,])
        lock.release()
        status = cursor.fetchone()
        if status==None:  #状态等于空，没找未观看的订单，那么这个订单失效了
            return HttpResponse("0")
        else:
            return HttpResponse("1")