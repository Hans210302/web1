"""xunying URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from myapp import views
from myapp import views_manager  #商家端使用
from myapp import alipay
from myapp import views,views10,suggestion
from myapp import view_biao


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/',views.login),
    path('register/',views.register),
    path('index/',views.index),
    path('select_seat/',views.select_seat),
    path('movie_detail/', views.movie_detail),
    path('movie/', views.movie),
    path('cinema/', views10.cinema),
    path('personal_center/', views10.personal_center),
    path('searchresult/', views.searchresult),
    path('compare/', views.compare),
    path('cinema_new/', views10.cinema_new),
    path('book_detail/', views.book_detail),
    path('comment/', views.comment),
    path('buyticket/', views.buyticket),
    path('password/', views.password),
    path('note/', views.note),
    path('buytoday/', views.buytoday),
    path('buytomorrow/', views.buytomorrow),
    path('buyaftertomorrow/', views.buyaftertomorrow),
    path('getseat/', views.getseat),
    path('getprice/', views.getprice),
    path('insertseat/', views.insertseat),
    path('write/', views.write),#评论
    path('wcomment/',views.wcomment),#写评论
    path('openpic/',views.openpic),#返回评论图片地址
    path('zhifu/',alipay.page1),#支付
    path('page2/',alipay.page2),#支付返回
    path('logout/',views10.logout),
    path('order_detail/', views.order_detail),  # 显示订单
    path('addOrder/', views.addOrder),  # 添加订单
    path('review/',view_biao.review),#短评
    path('myorder/',views10.myorder),
    path('zan/',view_biao.zan),
    path('delete/',views10.delete),
    path('mypoint/', views10.mypoint),
    path('reply/',view_biao.reply),
    path('make/',view_biao.make),
    path('totle/',view_biao.totle),
    path('new/',view_biao.new),
    path('hoot/',view_biao.hoot),
    path('check_movie/',views.check_movie),
    path('long_comment_add/',views.long_comment_add),
    path('long_comment_sub/',views.long_comment_sub),
    path('check_phone/',views.check_phone),  #检查手机号是否注册
    path('suggest/',suggestion.suggest),
    path('ceshi1/', view_biao.ceshi1),
    path('movie_suggest/', suggestion.movie_suggest),
    path('yuying/', view_biao.yuying),
    # path('page404/', view_biao.yuying),


    # ===============商家板块=======勿删===========
    path('manager/', views_manager.manager),
    path('field_manage/', views_manager.field_manage),
    path('movie_manage/', views_manager.movie_manage),
    path('cinema_manage/', views_manager.cinema_manage),
    path('edit_field/', views_manager.edit_field),
    path('outline/', views_manager.outline),
    path('outlinejudge/', views_manager.outlinejudge),  #下线判断
    path('delete_field/', views_manager.delete_field),
    path('online/', views_manager.online),
    path('chonline/', views_manager.chonline),  #选择电影上线
    path('add_field/', views_manager.add_field),  #增加场次
    path('cinema_manage/', views_manager.cinema_manage),  #增加场次
    path('order_manage/', views_manager.order_manage),  #订单管理
    path('seat_manage/', views_manager.seat_manage),  #订单管理
    path('show_userinfo/', views10.show_userinfo),  #显示用户信息
    path('del_longcomment/', views10.del_longcomment),  # 删除长影评
    path('del_comment/', views10.del_comment),  #删除短影评
    path('judge_status/', views_manager.judge_status),  #订单管理




    # ===============商家板块=======勿删===========
]
handler404=view_biao.page404