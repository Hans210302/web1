from bs4 import BeautifulSoup as bs
from urllib.error import HTTPError
from urllib.request import urlopen
import json
import pygal
import pymysql
db = pymysql.connect("localhost", "root", "970701", "xunying",charset='utf8')
cursor = db.cursor()

# 打开网页，获取源码
def open_page(url):
    try:
        netword = urlopen(url)
    except HTTPError as hp:
        print(1)
    else:
        # 采用BeautifulSoup来解析，且指定解析器
        html = bs(netword, 'lxml')
        return html


# 获取网页数据
def get_page(url):
    # 电影名称，上映天数，电影总票房，票房占比，排片场次，排片占比，场均人次，上座率
    movieName, releaseInfo, sumBoxInfo, boxInfo, boxRate, showInfo, showRate, avgShowView, avgSeatView = [], [], [], [], [], [], [], [], []
    html = open_page(url)
    p = html.find('p')
    text = p.get_text()
    # 将数据转换为python能够处理的格式
    jsonObj = json.loads(text)
    # 获取字典里面特定的键对应的键值
    data = jsonObj.get('data')
    # 想要的数据就在字典的键"list"对应的值
    lists = data.get('list')
    # print(type(lists)==type([]))判断类型
    for list in lists:
        # 获取字典里面特定的键对应的键值,并存储到列表中去
        movieName.append(list.get('movieName'))
        releaseInfo.append(list.get('releaseInfo'))
        sumBoxInfo.append(list.get('sumBoxInfo'))
        boxInfo.append(list.get('boxInfo'))
        boxRate.append(list.get('boxRate'))
        showInfo.append(list.get('showInfo'))
        showRate.append(list.get('showRate'))
        avgShowView.append(list.get('avgShowView'))
        avgSeatView.append(list.get('avgSeatView'))
    sql = "delete from Ticket"
    cursor.execute(sql)
    db.commit()
    for i in range(len(movieName)):
        sql = "INSERT INTO Ticket(Ticket_score,movie_name)VALUES('%s','%s')"%(boxInfo[i],movieName[i])
        cursor.execute(sql)
        print(movieName[i],boxInfo[i])
    db.commit()
    sql = "update Ticket,Movie set Ticket.Ticket_Movie_id=Movie.Movie_id where  Movie.Movie_name like CONCAT('%',Ticket.movie_name ,'%') "
    cursor.execute(sql)
    db.commit()
    return movieName, releaseInfo, sumBoxInfo, boxInfo, boxRate, showInfo, showRate, avgShowView, avgSeatView


# 利用pygal可视化数据
# 1-画出数据图.svg
def creat_BoxInfo(movieName, sumBoxInfo, title):
    # 设置坐标的旋转角度
    sum_pl = pygal.Bar(x_label_rotation=45, show_legend=False)
    sum_pl.title = title + "(万)"
    sum_pl.x_labels = movieName
    sum_pl.add('', sumBoxInfo)
    sum_pl.render_to_file('猫眼电影' + title + '.svg')


# 处理总票房数据
def get_piaofang(sumBoxInfos):
    # 列表存放处理的票房数据
    sumBoxInfos_piaofang = []
    for sumBoxInfo in sumBoxInfos:
        # 找到票房里面的中文的索引值
        index_yi = sumBoxInfo.find('亿')
        index_wan = sumBoxInfo.find('万')
        if index_yi != -1:
            # 对数据进行切片，而且字符串数据中存在点(.),不能直接转换为int，先转为float
            sumBoxInfo = int(float(sumBoxInfo[:index_yi]) * 10000000) / 10000
            sumBoxInfos_piaofang.append(sumBoxInfo)
        elif index_wan != -1:
            sumBoxInfo = int(float(sumBoxInfo[:index_yi]) * 10000) / 10000
            sumBoxInfos_piaofang.append(sumBoxInfo)
    return sumBoxInfos_piaofang


# 处理综合票房数据
def get_boxInfos_general_piaofang(boxInfos):
    boxInfos_piaofang = []
    for boxInfo in boxInfos:
        boxInfos_piaofang.append(int(float(boxInfo) * 10000) / 10000)
    return boxInfos_piaofang


url = 'https://box.maoyan.com/promovie/api/box/second.json'
# Movie_name, releaseInfo, sumBoxInfos, boxInfos, boxRate, showInfo, showRate, avgShowView, avgSeatView = get_page(url)
# sumBoxInfos_piaofang = get_piaofang(sumBoxInfos)
# boxInfos_piaofang = get_boxInfos_general_piaofang(boxInfos)
# creat_BoxInfo(movieName, sumBoxInfos_piaofang, '票房')
# creat_BoxInfo(movieName, boxInfos_piaofang, '综合票房')
