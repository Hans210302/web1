$(function(){
    var ur=location.href;//获取地址
    var type=ur.split('?')[1].split("=")[1];
    $("#"+type).trigger("click");//执行点击事件
});

