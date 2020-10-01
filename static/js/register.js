//用户名验证
function checkname(){
    var div1 = document.getElementById("div1");
    div1.innerHTML = "";
    var name1 = document.register.uname.value;
    if (name1 == "") {
    div1.innerHTML = "用户名不能为空！";
    return false;
}
    if (name1.length < 4 || name1.length > 16) {
    div1.innerHTML = "长度4-16个字符";
    return false;
}
    var charname1 = name1.toLowerCase();
    for (var i = 0; i < name1.length; i++) {
    var charname = charname1.charAt(i);
    if (charname=="!" || charname=="?" || charname=="。" || charname=="." || charname=="/" ) {
        div1.innerHTML = "用户名包含非法字符！";
        return false;
    }
}
    return true;
}

//手机号验证
function checkphone(){
    var div2 = document.getElementById("div2");
    div2.innerHTML = "";
    var phone1 = document.register.uphone.value;
    if (phone1 == "") {
    div2.innerHTML = "手机号不能为空！";
    return false;
}
    if (phone1.length!=11) {
    div2.innerHTML = "请输入正确手机号！";
    return false;
}
    var charphone1 = phone1.toLowerCase();
    for (var i = 0; i < phone1.length; i++) {
    var charphone = charphone1.charAt(i);
    if (!(charphone >= 0 && charphone <= 9)) {
        div2.innerHTML = "包含非法字符！";
        return false;
    }
}

var post_data={"phone1":phone1,};
    html=$.ajax({
        url: "/myapp/check_phone/",
        type: 'POST',
        data:post_data,
        success: function (data) {
            if (data=="1"){
            div2.innerHTML = "该手机号已注册！";
            return false;
            }
            else{
                 return true ;
            }

        },
        error:function () {
            return false;
            }
    })
    return true;
}

//验证码验证
function checkcode() {
    var div3 = document.getElementById("div3");
    div3.innerHTML = "";
    var num = document.register.use.value;
    if (num == "") {
        div3.innerHTML = "验证码不能为空！";
        return false;
    }else{
        $.ajax({
            url: "/myapp/note/",
            type: 'POST',
            data: {'num':num},
            success:function (data) {
                console.log(data);
                if (data =='false'){
                    div3.innerHTML = "验证码输入错误！";
                    return false;
                }else{
                    return true;
                }
            }
        })
    }
}

//密码验证
function checkpassword(){
    var div4 = document.getElementById("div4");
    div4.innerHTML = "";
    var password = document.register.password1.value;
    if (password == "") {
    div4.innerHTML = "密码不能为空";
    return false;
}
    if (password.length < 4 || password.length > 16) {
    div4.innerHTML = "密码长度为4-16位";
    return false;
    }
    return true;
}

function checkrepassword(){
    var div5 = document.getElementById("div5");
    div5.innerHTML = "";
    var password = document.register.password1.value;
    var repass = document.register.password2.value;
    if (repass == "") {
    div5.innerHTML = "密码不能为空";
    // document.register.password2.focus();
    return false;
}
    if (password != repass) {
    div5.innerHTML = "密码不一致";
    return false;
}
    return true;
}

function check(){
if (checkname() && checkphone() &&checkpassword() &&checkrepassword()) {
return true;
}
else {
return false;
}
}