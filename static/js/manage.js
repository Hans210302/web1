 $(document).ready(function () {
        $("#btnDialog").click(function () {
            $.DialogBySHF.Dialog({ Width: 1024, Height: 500, Title: "站长素材", URL: 'http://sc.chinaz.com' });
        })
    })

    function test() {
    var Movie_id=document.getElementById("out_movie_id").innerHTML;
    var post_data={"Movie_id":Movie_id,};
    html=$.ajax({
        url: "/myapp/outline/",
        type: 'POST',
        data:post_data,
        success: function (data) {
            if (data=="1") {
                window.location.reload();
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '下线成功！'});

            }
            else{
                $.DialogBySHF.Confirm({ Width: 350, Height: 200, Title: "提示", Content: '下线失败!'});

            }
        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })
    }
    function testCancel() {
         }

// 电影下线
function tips(th){
    var Movie_id=th.id;
    var post_data={"Movie_id":Movie_id,};
    document.getElementById("out_movie_id").innerHTML=Movie_id
    html=$.ajax({
        url: "/myapp/outlinejudge/",
        type: 'POST',
        data:post_data,
        success: function (data) {
            if (data=="1") {
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '您好，电影还有部分场次在放映！无法下线'});
            }
            else{
                $.DialogBySHF.Confirm({ Width: 350, Height: 200, Title: "提示", Content: '确定要下线这部电影吗?', ConfirmFun: test, CancelFun: testCancel });
            }
        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })
}

function edit_cfilm_info(th){
    var Cfilm_id=th.id.split("k")[0];
    date=document.getElementsByName("date")[0].value;
    time=document.getElementsByName("time")[0].value;
    hall=document.getElementsByName("hall")[0].value;
    price=document.getElementsByName("price")[0].value;
    var post_data={"Cfilm_id":Cfilm_id,"date":date,"time":time,"hall":hall,"price":price};
    html=$.ajax({
        url: "/myapp/edit_field/",
        type: 'POST',
        data:post_data,
        async: false,
        success: function (data) {
            if (data=="1") {
                 $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '保存成功！'});
            }
            else{
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '保存失败！'});
            }
        },
        error:function () {
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '保存失败！稍后再试'});
            }
    })
}

function onlinetips(th){
    var Movie_id=th.id;
    var post_data={"Movie_id":Movie_id,};
    html=$.ajax({
        url: "/myapp/chonline/",
        type: 'POST',
        data:post_data,
        async: false,
        success: function (data) {
            if (data=="1") {
                 $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '电影已在列表中！'});
            }
            else{
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '上线成功！'});
            }
        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })

}

function add_field(th){
    $('.theme-popover-mask').fadeIn(100);
    $('.theme-popover').slideDown(200);
    var movie_id=th.id;
    var Movie_id=movie_id.split('*')[0];
    $("#field_Movie_id").html(Movie_id);
}

function reset() {
     //重置
    document.getElementById("field_Movie_id").innerHTM="";
    document.getElementsByName("date_year")[0].value="";
    document.getElementsByName("date_month")[0].value="";
    document.getElementsByName("date_day")[0].value="";
    document.getElementsByName("time_hour")[0].value="";
    document.getElementsByName("time_minute")[0].value="";
    document.getElementsByName("hall")[0].value="";
    document.getElementsByName("price")[0].value="";
}

function commit_add_field(){
    var Movie_id=document.getElementById("field_Movie_id").innerHTML;
    var date=document.getElementsByName("date")[0].value;
    var time=document.getElementsByName("time")[0].value;
    var hall=document.getElementsByName("hall")[0].value;
    var price=document.getElementsByName("price")[0].value;
    var post_data={"Movie_id":Movie_id,"date":date,"time":time,"hall":hall,"price":price};
    html=$.ajax({
        url: "/myapp/add_field/",
        type: 'POST',
        data: post_data,
        success: function (data) {
            if (data=="1") {
                clo();
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '增加场次成功！'});
                reset()
            }
            else{
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '增加场次失败！'});
                reset()
            }
        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })
}

function clo() {
        $('.theme-popover-mask').fadeOut(100);
    $('.theme-popover').slideUp(200);
}




