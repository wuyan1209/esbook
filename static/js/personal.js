$(function () {
    // 查找用户的信息
    $.ajax({
        url: "/getUser/",
        type: "POST",
        async: false,
        dataType: "json",
        success: function (data) {
            // 填写个人信息
            var str = "../static/assets/images/users/" + data.result[5];
            $(".img").attr("src", str);
            $("#name").val(data.result[2]);
            $("#password").val("1234567");
            if (data.result[4] == "" || data.result[4]==null) {
                $("#phone").text("未绑定");
                $("#phone").addClass("dis");
            } else {
                $("#phone").text(data.result[4]);
            }
            if (data.result[3] == "" || data.result[3]==null) {
                $("#email").text("未绑定");
                $("#email").addClass("dis");
                $(".bind").attr("hidden",false);
                $(".edit").attr("hidden",true);
            } else {
                $("#email").text(data.result[3]);
                $(".edit").attr("hidden",false);
                $(".bind").attr("hidden",true);
            }
        }
    })

});

// 图片改变时
$('.input').bind("change", function () {
    var res = $(".input").val()
    if (res == null || res == " ") {
        $("#span").text("请选择图片");
        Time();
    } else {
        var extStart = res.lastIndexOf(".");
        var ext = res.substring(extStart, res.length).toUpperCase();
        if (ext != ".BMP" && ext != ".PNG" && ext != ".GIF" && ext != ".JPG" && ext != ".JPEG") {
            $("#span").text("图片限于png,gif,jpeg,jpg格式");
            Time();
        } else {
            /*提交表单*/
            document.form.submit();
        }
    }
});

//密码模态框隐藏时清空input
$('#editorPassword').on('hide.bs.modal', function () {
    $("#pwd").val("");
    $("#npwd").val("");
    $("#npwd2").val("");
});

function Time() {
    window.setTimeout(function () {
        $("#span").text(" ");
    }, 1000);
     window.setTimeout(function () {
        $("#msg0").text(" ");
    }, 2000);
    window.setTimeout(function () {
        $("#msg1").text(" ");
    }, 2000);
    window.setTimeout(function () {
        $("#msg2").text(" ");
    }, 2000);
    window.setTimeout(function () {
        $("#emsg1").text(" ");
    }, 2000);
    window.setTimeout(function () {
        $("#emsg2").text(" ");
    }, 2000);
}

//修改密码
function modifyPwd() {
    var pwd = $("#pwd").val();
    var npwd = $("#npwd").val();
    var npwd2 = $("#npwd2").val();
    if (pwd && npwd && npwd2) {
        //1.判断原密码是否正确
        $.ajax({
            url: "/conpwd/",
            type: "POST",
            data: {
                "password": pwd
            },
            async: false,
            dataType: "json",
            success: function (data) {
                if (data.status != 200) {
                    $("#msg1").text(data.message);
                    Time();
                } else {
                    //2.判断两次输入的密码是否一样
                    if (npwd2 != npwd) {
                        $("#msg2").text("两次输入密码不一致");
                        Time();
                    } else {
                        //3.修改密码
                        $.ajax({
                            url: "/modifyPwd/",
                            type: "POST",
                            async: false,
                            data: {
                                "npassword":npwd
                            },
                            dataType: "json",
                            success: function (data) {
                                if(data.status==200){
                                     window.location.href='/personal/';
                                }else{
                                    $("#msg0").text(data.message);
                                    Time();
                                }
                            }
                        })
                    }
                }
            }
        })
    }

}

 //绑定邮箱的邮箱校验
$("#inputEmail1").blur(function () {
    var emreg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/; //邮箱验证规则
    var email = $("#inputEmail1").val();//邮箱号
    var tmp = emreg.test(email);
    if (tmp == false) {
        $("#email1").text("请输入正确的邮箱号");
    } else {
        $.ajax({
             url: "/valiEmail/",
             type: "POST",
             data: {
                 "email": email,
             },
             dataType: "json",
             success: function (data) {
                 if (data.status == 2001) {
                     $("#email1").text("邮箱号已被绑定过");
                     $("#emailCodeBtn1").attr("disabled",true)
                 } else {
                     $("#email1").text(" ");
                     $("#eCode1").text(" ");
                     $("#emailCodeBtn1").removeAttr("disabled")
                 }
             }
         })
    }
});
 //绑定邮箱的邮箱验证码校验
$("#inputEmailCode1").blur(function () {
    var email = $("#emsg1").text();//邮箱验证码
    var code=$("#inputEmailCode1").val(); //输入的验证码
    if(email==code){
        $("#eCode1").text(" ");
    }else{
        $("#eCode1").text("验证码不正确");
    }
});
//绑定邮箱的获取邮箱验证码
function emailCode1() {
    var email=$("#inputEmail1").val() //邮箱号
    var msg=$("#email1").text(); //提示信息
    if(email && msg==" "){
        $("#eCode1").text(" ");
        $.ajax({
            url: "/postEmail/",
            type: "POST",
            data: {
                "email": email,
            },
            dataType: "json",
            success: function (data) {
                if (data.status == 200) {
                    $("#code1").text(data.message);
                    $("#inputEmailCode1").focus()
                } else {
                    $("#eCode1").text(data.message)
                }
            }
        })
    }else{
        $("#email1").text("请填写正确的邮箱后再获取验证码");
    }
}
//绑定邮箱的模态框隐藏时清空input和span
$('#addEmail').on('hide.bs.modal', function () {
    $("#inputEmail1").val("");
    $("#inputEmailCode1").val("");
    $("#eCode1").text(" ");
    $("#email1").text(" ");
    $("#msg1").text(" ");
});
//绑定邮箱
function bindEmail() {
    var email = $("#inputEmail1").val() //邮箱号
    var msg = $("#email1").text(); //邮箱提示信息
    var code=$("#eCode1").text();  //邮箱验证码提示信息
    if (email && msg == " " && code==" ") {
        $("#eCode1").text(" ");
        $.ajax({
            url: "/bindEmail/",
            type: "POST",
            data: {
                "email": email,
            },
            dataType: "json",
            success: function (data) {
                if (data.status == 200) {
                    window.location.href = '/personal/';
                } else {
                    $("#emsg1").text(data.message);
                    Time();
                }
            }
        })
    } else {
        return false;
    }
}


 //修改邮箱的邮箱校验
$("#inputEmail2").blur(function () {
    var emreg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/; //邮箱验证规则
    var email = $("#inputEmail2").val();//邮箱号
    var tmp = emreg.test(email);
    if (tmp == false) {
        $("#email2").text("请输入正确的邮箱号");
    } else {
        $.ajax({
             url: "/valiEmail/",
             type: "POST",
             data: {
                 "email": email,
             },
             dataType: "json",
             success: function (data) {
                 if (data.status == 2001) {
                     $("#email2").text("邮箱号已被绑定过");
                     $("#emailCodeBtn2").attr("disabled",true)
                 } else {
                     $("#email2").text(" ");
                     $("#eCode2").text(" ");
                     $("#emailCodeBtn2").removeAttr("disabled")
                 }
             }
         })
    }
});
 //修改邮箱的邮箱验证码校验
$("#inputEmailCode2").blur(function () {
    var email = $("#emsg2").text();//邮箱验证码
    var code=$("#inputEmailCode2").val(); //输入的验证码
    if(email==code){
        $("#eCode2").text(" ");
    }else{
        $("#eCode2").text("验证码不正确");
    }
});
//修改邮箱的获取邮箱验证码
function emailCode2() {
    var email=$("#inputEmail2").val() //邮箱号
    var msg=$("#email2").text(); //提示信息
    if(email && msg==" "){
        $("#eCode2").text(" ");
        $.ajax({
            url: "/postEmail/",
            type: "POST",
            data: {
                "email": email,
            },
            dataType: "json",
            success: function (data) {
                if (data.status == 200) {
                    $("#code2").text(data.message);
                    $("#inputEmailCode2").focus()
                } else {
                    $("#eCode2").text(data.message)
                }
            }
        })
    }else{
        $("#email1").text("请填写正确的邮箱后再获取验证码");
    }
}
//修改邮箱的模态框隐藏时清空input和span
$('#editorEmail').on('hide.bs.modal', function () {
    $("#inputEmail2").val("");
    $("#inputEmailCode2").val("");
    $("#eCode2").text(" ");
    $("#email2").text(" ");
    $("#msg2").text(" ");
});
//修改邮箱
function editorEmail() {
    var email = $("#inputEmail2").val() //邮箱号
    var msg = $("#email2").text(); //邮箱提示信息
    var code=$("#eCode2").text();  //邮箱验证码提示信息
    if (email && msg == " " && code==" ") {
        $("#eCode2").text(" ");
        $.ajax({
            url: "/bindEmail/",
            type: "POST",
            data: {
                "email": email,
            },
            dataType: "json",
            success: function (data) {
                if (data.status == 200) {
                    window.location.href = '/personal/';
                } else {
                    $("#emsg2").text(data.message);
                    Time();
                }
            }
        })
    } else {
        return false;
    }
}