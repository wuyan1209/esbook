//切换邮箱手机号找回
function Switch() {
    if ($(".switch").text() == '使用邮箱找回') {
        //手机号换为邮箱
        $("#myPhone").css("display", "none");
        $("#phoneCode").css("display", "none");
        $("#inputPhone").removeAttr("required");
        $("#inputPhoneCode").removeAttr("required");
        $("#myEmail").css("display", "block");
        $("#emailCode").css("display", "block");
        $("#inputEmail").attr("required", "true");
        $("#inputEmailCode").attr("required", "true");
        $("#phone").text(" ");
        $("#pCode").text(" ");
        $("#inputPhone").val(" ");
        $(".switch").text("使用手机找回");
    } else {
        //邮箱换为手机号
        $("#myPhone").css("display", "block");
        $("#phoneCode").css("display", "block");
        $("#inputPhone").attr("required", "true");
        $("#inputPhoneCode").attr("required", "true");
        $("#myEmail").css("display", "none");
        $("#emailCode").css("display", "none");
        $("#inputEmail").removeAttr("required");
        $("#inputEmailCode").removeAttr("required");
        $("#email").text(" ");
        $("#eCode").text(" ");
        $("#inputEmail").val(" ");
        $(".switch").text("使用邮箱找回");
    }
}

//邮箱校验
$("#inputEmail").blur(function () {
    var emreg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/; //邮箱验证规则
    var email = $("#inputEmail").val();//邮箱号
    var tmp = emreg.test(email);
    if (tmp == false) {
        $("#email").text("请输入正确的邮箱号");
        $("#emailCodeBtn").attr("disabled", true)
    } else {
        $("#email").text(" ");
        $("#emailCodeBtn").removeAttr("disabled")
    }
});

//获取邮箱验证码
function emailCode() {
    var email = $("#inputEmail").val() //邮箱号
    var msg = $("#email").text(); //提示信息
    if (email && msg == " ") {
        $("#eCode").text(" ");
        $.ajax({
            url: "/postEmail/",
            type: "POST",
            data: {
                "email": email,
            },
            dataType: "json",
            success: function (data) {
                if (data.status == 200) {
                    $("#msg").text(data.message);
                    $("#inputEmailCode").focus()
                } else {
                    $("#eCode").text(data.message)
                }
            }
        })
    } else {
        $("#email").text("请填写正确的邮箱后再获取验证码");
    }
}

//邮箱验证码校验
$("#inputEmailCode").blur(function () {
    var email = $("#msg").text();//邮箱验证码
    var code = $("#inputEmailCode").val(); //输入的验证码
    if (email == code) {
        $("#eCode").text(" ");
    } else {
        $("#eCode").text("验证码不正确");
    }
});


//找回密码校验
function checkForm() {
    var phoneMsg = $("#phone").text();
    var pCodeMsg = $("#pCode").text();
    var emailMsg = $("#email").text();
    var eCodeMsg = $("#eCode").text();
    var pwd = $("#inputPassword").val();
    var email = $("#inputEmail").val();
    if (phoneMsg == " " && emailMsg == " " && pCodeMsg == " " && eCodeMsg == " ") {
        $.ajax({
            url: "/updatePwd/",
            type: "POST",
            async: false,
            data: {
                "pwd": pwd,
                "email":email
            },
            dataType: "json",
            success: function (data) {
                if (data.status == 200) {
                    window.location.href = '/resetPassword/';
                } else {
                    $("#msg0").text(data.message);
                    Time();
                }
            }
        })
    } else {
        return false;
    }
}


function Time() {
     window.setTimeout(function () {
        $("#msg0").text(" ");
    }, 2000);
}