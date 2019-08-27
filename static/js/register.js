//跳转到登录页面
function Login() {
    window.location.href = '/login/'
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
//表单验证
function validation() {

}