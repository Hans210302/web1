var ur=location.href;//获取地址
var Movie_id=ur.split('?')[1].split("&")[0].split("=")[1];  //获取电影id
var post_data={"Movie_id":Movie_id};
html=$.ajax({
    url: "/myapp/check_movie/",
    type: 'POST',
    data:post_data,
    success: function (data) {
        if(data=="1"){
            $('#buy_ticket').show();
        }
        else{
            $('#buy_ticket').hide();

        }

    },
    error:function () {
            alert("服务器请求超时,请重试!")
        }
})

