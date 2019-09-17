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
            } else {
                $("#email").text(data.result[3]);
            }
        }
    })


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