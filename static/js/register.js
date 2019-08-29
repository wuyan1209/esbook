//跳转到登录页面
function Login() {
    window.location.href = '/login/';
}
//切换邮箱手机号注册
function Switch() {
    if ($(".switch").text() == '使用邮箱注册') {
        //手机号换为邮箱
        $("#myPhone").css("display", "none");
        $("#code").css("display", "none");
        $("#inputPhone").removeAttr("required");
        $("#inputCode").removeAttr("required");
        $("#myEmail").css("display", "block");
        $("#inputEmail").attr("required","true");
        $(".switch").text("使用手机注册");
    } else {
        //邮箱换为手机号
        $("#myPhone").css("display", "block");
        $("#code").css("display", "block");
        $("#inputPhone").attr("required","true");
        $("#inputCode").attr("required","true");
        $("#myEmail").css("display", "none");
        $("#inputEmail").removeAttr("required");
        $(".switch").text("使用邮箱注册");
    }
}

//用户名数据库校验
 $("#inputName").blur(function () {
     var name = $("#inputName").val();
     $.ajax({
         url: "/valiName/",
         type: "POST",
         data: {
             "name": name,
         },
         dataType: "json",
         success: function (data) {
             if (data.status == 2001) {
                 $("#name").text("用户名已被占用");
                 $("#phone").text(" ");
                 $("#email").text(" ");
             } else {
                 $("#name").text(" ");
             }
         }
     })
 });
//手机号校验
 $("#inputPhone").blur(function () {
     var reg = /^1[3|4|5|7|8][0-9]{9}$/; //手机号验证规则
     var phoneNum = $("#inputPhone").val();//手机号码
     var flag = reg.test(phoneNum);
     if (flag == false) {
         $("#phone").text("请输入正确的手机号");
     } else {
         $.ajax({
             url: "/valiPhone/",
             type: "POST",
             async: false,
             data: {
                 "phone": phoneNum,
             },
             dataType: "json",
             success: function (data) {
                 if (data.status == 2001) {
                     $("#phone").text("手机号已被占用");
                     $("#name").text(" ");
                     $("#email").text(" ");
                 } else {
                     $("#phone").text(" ");
                 }
             }
         })
     }
 });
 //邮箱校验
$("#inputEmail").blur(function () {
    var emreg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/; //邮箱验证规则
    var email = $("#inputEmail").val();//邮箱号
    var tmp = emreg.test(email);
    if (tmp == false) {
        $("#email").text("请输入正确的邮箱号");
    } else {
        $.ajax({
             url: "/valiEmail/",
             type: "POST",
             async: false,
             data: {
                 "email": email,
             },
             dataType: "json",
             success: function (data) {
                 if (data.status == 2001) {
                     $("#email").text("邮箱号已被占用");
                     $("#name").text(" ");
                     $("#phone").text(" ");
                 } else {
                     $("#email").text(" ");
                 }
             }
         })
    }
});

//注册
function checkForm() {
    var phoneNum = $("#inputPhone").val();//手机号码
    //var code=$("#inputCode").val();//短信验证码
    var email = $("#inputEmail").val();//邮箱号
    var name = $("#inputName").val();//用户名
    var password = $("#inputPassword").val();//密码
    if(!(name && password && (phoneNum || email))){
        return false;
    }
}