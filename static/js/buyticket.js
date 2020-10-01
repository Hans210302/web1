function buytoday() {
    var ur=location.href;//获取地址
    var Cinema_id=ur.split('?')[1].split("&")[0].split("=")[1];  //获取影院id
    var Movie_id=ur.split('?')[1].split("=")[2];  //获取电影id
    var post_data={"Cinema_id":Cinema_id,"Movie_id":Movie_id};
    html=$.ajax({
        url: "/myapp/buytoday/",
        type: 'POST',
        data:post_data,
        success: function (html) {
            $('#today').html(html)
        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })
}

function buytomorrow() {
    var ur=location.href;//获取地址
    var Cinema_id=ur.split('?')[1].split("&")[0].split("=")[1];  //获取影院id
    var Movie_id=ur.split('?')[1].split("=")[2];  //获取电影id
    var post_data={"Cinema_id":Cinema_id,"Movie_id":Movie_id}
    $.ajax({
        url: "/myapp/buytomorrow/",
        type: 'POST',
        data:post_data,
        success: function (html) {
            $('#tomorrow').html(html)
        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })
}

function buyaftertomorrow() {
    var ur=location.href;//获取地址
    var Cinema_id=ur.split('?')[1].split("&")[0].split("=")[1];  //获取影院id
    var Movie_id=ur.split('?')[1].split("=")[2];  //获取电影id
    var post_data={"Cinema_id":Cinema_id,"Movie_id":Movie_id}
    $.ajax({
        url: "/myapp/buyaftertomorrow/",
        type: 'POST',
        data:post_data,
         success: function (html) {
            $('#aftertomorrow').html(html)
        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })
}

function GetDateStr(AddDayCount)
{
var dd = new Date();
dd.setDate(dd.getDate()+AddDayCount);//获取AddDayCount天后的日期
var y = dd.getYear()+1900;
var m = dd.getMonth()+1;//获取当前月份的日期
var d = dd.getDate();
return y+"-"+m+"-"+d;
}
