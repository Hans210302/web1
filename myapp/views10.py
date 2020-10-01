from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
import pymysql
import json
import time
from django.utils.timezone import now, timedelta
import threading
from qiniu import Auth


conn = pymysql.connect(host='localhost', user='root', passwd='970701', db='xunying', charset='utf8')  #连接数据库
cursor = conn.cursor(pymysql.cursors.DictCursor)
lock = threading.Lock() #Lock对象
today = now().date() + timedelta(days=0)  # 今天
time=time.strftime('%H:%M',time.localtime(time.time())) #当前时间

#影院查询
def cinema_new(request):
    if  request.method == "GET":
        # 查询影院
        cursor.execute("select * from Cinema ")
        Movie_cinema_list = cursor.fetchall()
        return render(request, 'cinema_new.html',{"Movie_cinema_list":Movie_cinema_list,})
    else:
        name1 = request.POST.get('name1')
        name2 = request.POST.get('name2')
        if name1 == '全部' and name2=='全部':
            lock.acquire()
            cursor.execute("select * from Cinema ")
            lock.release()
            Movie_cinema_list = cursor.fetchall()
        elif name1 == '全部' and name2!='全部':
            name2 = '%' + name2 + '%'
            lock.acquire()
            cursor.execute("select * from Cinema where Cinema_address like '%s' " % name2)
            lock.release()
            Movie_cinema_list = cursor.fetchall()
        elif name2 == '全部' and name1!='全部':
            name1 = '%' + name1 + '%'
            lock.acquire()
            cursor.execute("select * from Cinema where Cinema_name like '%s' " % name1)
            lock.release()
            Movie_cinema_list = cursor.fetchall()
        else:
            name1 = '%' + name1 + '%'
            name2 = '%' + name2 + '%'
            lock.acquire()
            cursor.execute("select * from Cinema where Cinema_address like '%s' and Cinema_name like '%s' " % (name2,name1))
            lock.release()
            Movie_cinema_list = cursor.fetchall()
        list1 = ''
        for row in Movie_cinema_list:
            list = '''
                          <tr>
                              <td style="width: 1250px"><h4>''' + str(row["Cinema_name"]) + '''</h4>
                                  <p style="width: 850px"> ''' + str(row["Cinema_address"]) + ''' </p>
                                  <p>距我：<input type="text" class='''+str(row['Cinema_id'])+''' value="" style="border: 0;background-color: rgba(255,251,251,0)" disabled></p></td>
                              <td><a href="/myapp/cinema/?Cinema_id=''' + str(row["Cinema_id"]) + '''"><input type="button" class="xunying_btn" value="寻影价：￥''' + str(row["Cinema_price"]) + ''' "></a>
                                  <p style="margin-left: 25px">猫眼价：￥''' + str(row["Cinema_mao"]) + '''</p>
                                  <p style="margin-left: 25px">淘宝价：￥''' + str(row["Cinema_tao"]) + '''</p>
                              </td>
                          </tr>
                          <script>
                            getPoint("'''+str(row["lng"])+'''","'''+str(row["lat"])+'''",".'''+str(row['Cinema_id'])+'''");
                        </script>
                      '''
            list1 = list1 + list
        return HttpResponse(list1)

def cinema(request):
    if  request.method == "GET":
        Cinema_id = request.GET.get("Cinema_id")
        lock.acquire()
        cursor.execute("select * from Cinema where Cinema_id=%s", [Cinema_id, ])
        lock.release()
        Cinema_list = cursor.fetchone()
        lock.acquire()
        cursor.execute("select * from Movie where Movie_id=any(select distinct Cfilm_Movie_id from Cinemafilm where Cfilm_Cinema_id=%s) ", [Cinema_id, ])
        lock.release()
        movive_list = cursor.fetchall()
        return render(request, 'cinema.html',{"Cinema_list":Cinema_list,"movive_list":movive_list})
    else:
        return render(request, 'cinema.html')

#注销登录
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/myapp/index/')

#个人中心
def personal_center(request):
    if request.method =="GET":
        session_id = request.session.get('USERID')
        # 需要填写你的 Access Key 和 Secret Key
        access_key = 'EjIqvG2iluFxOx-PzeIyCNUKqUL2je9Q5bfunOyg'
        secret_key = 'pqt97zqOt7cw07a9AWwEXPp0zofB_9swvTVJGOOr'
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 要上传的空间
        bucket_name = 'xunyingpicture'
        # 上传到七牛后保存的文件名
        key = None
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key, 3600)
        return render(request, 'personal_center.html', {'token': token, 'session_id': session_id})
    else:
        session_id = request.session.get('USERID')
        name = request.POST.get('name')
        request.session["USERNAME"] = name
        sex = request.POST.get('sex_val')
        birth = request.POST.get('birth')
        note = request.POST.get('note')
        src = request.POST.get('img_src')
        label = "-".join(json.loads(request.POST.getlist("label_val")[0]))
        cursor.execute("Update User set User_name=%s,User_sex=%s,User_birth=%s,User_note=%s,User_label=%s,User_pic=%s where User_id=%s",
            [name, sex, birth, note, label,src,session_id])
        conn.commit()
        return HttpResponse("OK")

#基本资料
def show_userinfo(request):
    session_id = request.session.get('USERID')
    lock.acquire()
    cursor.execute("select * from User where User_id=%s", [session_id, ])
    lock.release()
    userinfo_list = cursor.fetchone()
    return HttpResponse(json.dumps({'userinfo_list': userinfo_list}, ensure_ascii=False))

#我的订单
def myorder(request):
    if request.method =="POST":
        session_id = request.session.get('USERID')
        nowtime = str(today)+ time
        lock.acquire()
        cursor.execute("select t_Order.Order_date,t_Order.Order_id,t_Order.Order_local,Cinemafilm.Cfilm_Movie_name,Cinemafilm.Cfilm_hall,Cinemafilm.Cfilm_date,Cinemafilm.Cfilm_time,Cinema.Cinema_name,Movie.Movie_picture,Cinemafilm.Cfilm_price*t_Order.Order_number as toltal_price from t_Order,Cinemafilm,Cinema,Movie where t_Order.Order_Cfilm_id=Cinemafilm.Cfilm_id and Cinemafilm.Cfilm_Cinema_id=Cinema.Cinema_id and Cinemafilm.Cfilm_Movie_id=Movie_id and t_Order.Order_user_id=%s" %(session_id))
        lock.release()
        order_list = cursor.fetchall()
        list1=''
        for row in order_list:
            thatime = row["Cfilm_date"] + row["Cfilm_time"]
            if nowtime<thatime:
                list = '''
                    <table id="''' + str(row["Order_id"]) + '''">
                        <tr style="height:30px;">
                            <td colspan="2" style="padding-left:30px">''' + str(row["Order_date"]) + '''</td>
                            <td>订单编号：<span id="orderid">''' + str(row["Order_id"]) + '''</span></td>
                            <td colspan="3" style="text-align:right;padding-right:20px;"><img src="../../static/image/delete.jpg" onclick="del(this)" alt="''' + str(row["Order_id"]) + '''" style="width:20px;height: 20px"></td>
                        </tr>
                        <tr>
                            <td style="padding-left:30px;width:150px;"><img src="''' + str(row["Movie_picture"]) + '''" style="width: 85px;height: 110px"></td>
                            <td style="line-height:12px;width:180px;"><p style="front-size:18px;"><strong>《''' + str(row["Cfilm_Movie_name"]) + '''》</strong></p>
                                <p>''' + str(row["Cinema_name"]) + '''</p>
                                <p>''' + str(row["Cfilm_hall"]) + '''</p>
                                <p style="color:red;">''' + str(row["Cfilm_date"]) + ''' ''' + str(row["Cfilm_time"]) + '''</p>
                            </td>
                            <td style="width:200px;">''' + str(row["Order_local"]) + '''</td>
                            <td>￥''' + str(row["toltal_price"]) + '''</td>
                            <td><img src="../../static/image/timein.png" alt="待观影" style="width:60px;height: 50px;"></td>
                            <td style="text-align: center"><a href="/myapp/book_detail/?Order_id=''' + str(row["Order_id"]) + '''">查看详情</a></td>
                        </tr>
                    </table>    
                    '''
                list1 = list1 + list
            else:
                list = '''
                    <table id="''' + str(row["Order_id"]) + '''">
                        <tr style="height:30px;">
                            <td colspan="2" style="padding-left:30px">''' + str(row["Order_date"]) + '''</td>
                            <td>订单编号：<span id="orderid">''' + str(row["Order_id"]) + '''</span></td>
                            <td colspan="3" style="text-align:right;padding-right:20px;"><img src="../../static/image/delete.jpg" onclick="del(this)" alt="''' + str(row["Order_id"]) + '''" style="width:20px;height: 20px"></td>
                        </tr>
                        <tr>
                            <td style="padding-left:30px;width:150px;"><img src="''' + str(row["Movie_picture"]) + '''" style="width: 85px;height: 110px"></td>
                            <td style="line-height:12px;width:180px;"><p style="front-size:18px;"><strong>《''' + str(row["Cfilm_Movie_name"]) + '''》</strong></p>
                                <p>''' + str(row["Cinema_name"]) + '''</p>
                                <p>''' + str(row["Cfilm_hall"]) + '''</p>
                                <p style="color:red;">''' + str(row["Cfilm_date"]) + ''' ''' + str(row["Cfilm_time"]) + '''</p>
                            </td>
                            <td style="width:200px;">''' + str(row["Order_local"]) + '''</td>
                            <td>￥''' + str(row["toltal_price"]) + '''</td>
                            <td><img src="../../static/image/timeout.png" alt="已失效" style="width:60px;height: 50px;"></td>
                            <td style="text-align: center"><a href="/myapp/book_detail/?Order_id=''' + str(row["Order_id"]) + '''">查看详情</a></td>
                        </tr>
                    </table>    
                '''
                list1 = list1 + list
        return HttpResponse(list1)
    else:
        return HttpResponse()

##删除订单
def delete(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        lock.acquire()
        cursor.execute("delete from t_Order where Order_id=%s",[order_id])
        lock.release()
        conn.commit()
        return HttpResponse('OK')
    else:
        return HttpResponse('error')

#我的发布
def mypoint(request):
    if request.method =="POST":
        session_id = request.session.get('USERID')
        lock.acquire()
        cursor.execute("select Movie.Movie_picture,Movie.Movie_id,Longcomment.Longcomment_title,Longcomment.Longcomment_id,Longcomment.Longcomment_date,Longcomment.Longcomment_content,Longcomment.Longcomment_like from Movie,Longcomment where Longcomment.Longcomment_Movie_id=Movie_id and Longcomment.Longcomment_User_id=%s"%(session_id))
        lock.release()
        comm_list1 = cursor.fetchall()
        lock.acquire()
        cursor.execute("select Movie.Movie_picture,Movie.Movie_id,Comment.Comment_id,Comment.Comment_date,Comment.Comment_content,Comment.Comment_like from Movie,Comment where Comment.Comment_Movie_id=Movie_id and Comment.Comment_User_id=%s"%(session_id))
        lock.release()
        comm_list2 = cursor.fetchall()
        list=''
        for row in comm_list1:
            list1 = '''
                <table id="''' + str(row["Longcomment_id"]) + '''">
                    <tr >
                        <td rowspan="2"  style="width:120px;margin:0px auto;padding-left:10px;"><a href="/myapp/movie_detail/?Movie_id=''' + str(row["Movie_id"]) + '''"><img src="''' + str(row["Movie_picture"]) + '''" style="width:100px;height:120px"></a></td>
                        <td ><p><strong>''' + str(row["Longcomment_title"]) + '''</strong>   ''' + str(row["Longcomment_date"]) + '''   赞(''' + str(row["Longcomment_like"]) + ''')&nbsp;&nbsp;</td>
                        <td><img src="../../static/image/delete.jpg" onclick="del_long(this)" alt="''' + str(row["Longcomment_id"]) + '''"  style="width:20px;height: 20px;"></p></td>
                    </tr>    
                    <tr>    
                        <td colspan="2" ><p>''' + str(row["Longcomment_content"][:170]) + '''</p>
                        <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="/myapp/reply/?Longcomment_id=''' + str(row["Longcomment_id"]) + '''">...<img src="../../static/image/conn.png" style="width:15px;height:15px">链接</a></p>   
                        </td>
                    </tr>
                </table>
                 '''
            list = list + list1
        for row in comm_list2:
            list2 = '''
                    <table id="''' + str(row["Comment_id"]) + '''">
                        <tr>
                            <td rowspan="2"  style="width:120px;margin:0px auto;padding-left:10px;"><a href="/myapp/movie_detail/?Movie_id=''' + str(row["Movie_id"]) + '''"><img src="''' + str(row["Movie_picture"]) + '''" style="width:100px;height:120px"></a></td>
                            <td style="height:30px;"><p>''' + str(row["Comment_date"]) + '''   赞(''' + str(row["Comment_like"]) + ''')</p></td>
                            <td style="text-align:right;"><img src="../../static/image/delete.jpg" onclick="del_short(this)" alt="''' + str(row["Comment_id"]) + '''"  style="width:20px;height: 20px;margin-right:30px"></p></td>
                        <tr>
                            <td><p>''' + str(row["Comment_content"]) + '''</p> </td>
                        </tr>
                    </table>
                '''
            list = list +list2
        return HttpResponse(list)
    else:
        return HttpResponse()

# 删除长影评
def del_longcomment(request):
    if request.method == "POST":
        longcomment_id = request.POST.get('longcomment_id')
        lock.acquire()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        lock.release()
        conn.commit()
        lock.acquire()
        cursor.execute("delete from Longcomment where Longcomment_id=%s",[longcomment_id])
        lock.release()
        conn.commit()
        # 删除回复
        lock.acquire()
        cursor.execute("delete from Reply where Reply_Longcomment_id=%s", [longcomment_id])
        lock.release()
        conn.commit()
        return HttpResponse('OK')
    else:
        return HttpResponse()


# 删除短影评
def del_comment(request):
    if request.method == "POST":
        comment_id = request.POST.get('comment_id')
        cursor.execute("delete from Comment where Comment_id=%s",[comment_id])
        conn.commit()
        return HttpResponse('OK')
    else:
        return HttpResponse("error")