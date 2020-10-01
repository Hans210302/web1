function logincheck(){
    var login_account=document.getElementById("login_account").value;
    var login_pwd=document.getElementById("login_pwd").value;
    var login_type=document.getElementById("login_type").value;
    var post_data={"login_account":login_account,"login_pwd":login_pwd,"login_type":login_type,};
    if (login_account.length ==0 || login_pwd.length ==0 ){
        $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '账户或密码不能为空!'});
    }
    else {
        html=$.ajax({
        url: "/myapp/login/",
        type: 'POST',
        data:post_data,
        success: function (data) {
            if (data=="0") {
                $.DialogBySHF.Alert({ Width: 350, Height: 200, Title: "提示", Content: '密码错误或用户不存在!'});
            }
            else if (data=="1") {
                var storage=window.localStorage;
                last_url=storage["last_url"];
                storage.clear();
                if (last_url!=null){
                    window.location.href =last_url
                }
                else{
                    window.location.href ="http://127.0.0.1:8000/myapp/index/"
                }

            }

            else if (data=="2") {
                window.location.href ="http://127.0.0.1:8000/myapp/field_manage/"
            }

        },
        error:function () {
                alert("服务器请求超时,请重试!")
            }
    })
    }



}