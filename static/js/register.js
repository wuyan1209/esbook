//跳转到登录页面
function Login() {
    window.location.href = '/login/';
}
//切换邮箱手机号注册
function Switch() {
    if ($(".switch").text() == '使用邮箱注册') {
        //手机号换为邮箱
        $("#myPhone").css("display", "none");
        $("#phoneCode").css("display", "none");
        $("#inputPhone").removeAttr("required");
        $("#inputPhoneCode").removeAttr("required");
        $("#myEmail").css("display", "block");
        $("#emailCode").css("display", "block");
        $("#inputEmail").attr("required","true");
        $("#inputEmailCode").attr("required","true");
        $("#phone").text(" ");
        $("#pCode").text(" ");
        $("#inputPhone").val(" ");
        $(".switch").text("使用手机注册");
    } else {
        //邮箱换为手机号
        $("#myPhone").css("display", "block");
        $("#phoneCode").css("display", "block");
        $("#inputPhone").attr("required","true");
        $("#inputPhoneCode").attr("required","true");
        $("#myEmail").css("display", "none");
        $("#emailCode").css("display", "none");
        $("#inputEmail").removeAttr("required");
        $("#inputEmailCode").removeAttr("required");
        $("#email").text(" ");
        $("#eCode").text(" ");
        $("#inputEmail").val(" ");
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
  //手机验证码校验
$("#inputPhoneCode").blur(function () {

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
                     $("#eCode").text()
                 }
             }
         })
    }
});
 //邮箱验证码校验
$("#inputEmailCode").blur(function () {
    var email = $("#msg").text();//邮箱验证码
    var code=$("#inputEmailCode").val(); //输入的验证码
    if(email==code){
        $("#eCode").text(" ");
    }else{
        $("#eCode").text("验证码不正确");
    }
});



//获取手机验证码
function phoneCode() {

}

//获取邮箱验证码
function emailCode() {
    var email=$("#inputEmail").val() //邮箱号
    var msg=$("#email").text(); //提示信息
    if(email && msg==" "){
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
    }else{
        $("#email").text("请填写正确的邮箱后再获取验证码");
    }
}


//注册校验
function checkForm() {
    var phoneMsg=$("#phone").text();
    var pCodeMsg=$("#pCode").text();
    var emailMsg=$("#email").text();
    var eCodeMsg=$("#eCode").text();
    var nameMsg=$("#name").text();
    if(phoneMsg==" " && emailMsg==" " && nameMsg==" " && pCodeMsg==" " && eCodeMsg==" "){
        return true;
    }else{
        return false;
    }
}