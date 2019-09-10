//校验
function checkLoginForm() {
    var username = $('#userName').val();
    var password = $('#password').val();
    if (isNull(username) && isNull(password)) {
        $('#submit').attr('value', '请输入手机号/邮箱和密码!!!').css('background', 'red');
        return false;
    }
    if (isNull(username)) {
        $('#submit').attr('value', '请输入手机号/邮箱!!!').css('background', 'red');
        return false;
    }
    if (isNull(password)) {
        $('#submit').attr('value', '请输入密码!!!').css('background', 'red');
        return false;
    }
    if (password.length<6){
        $('#submit').attr('value', '密码至少6位!!!').css('background', 'red');
        return false;
    }
    if (username.search("@") != -1) {
        //邮箱校验
        var emreg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+/; //邮箱验证规则
        var tmp = emreg.test(username);
        if (tmp == false) {
            $('#submit').attr('value', '请输入正确的邮箱号!!!').css('background', 'red');
            return false;
        }
    }
    if (username.search("@") == -1) {
        //手机校验
        var reg = /^1[3|4|5|7|8][0-9]{9}$/; //手机号验证规则
        var flag = reg.test(username);
        if (flag == false) {
            $('#submit').attr('value', '请输入正确的手机号!!!').css('background', 'red');
            return false;
        }
    } else {
        $('#submit').attr('value', 'Logining~');
        return true;
    }


}

//是否为空
function isNull(input) {
    if (input == null || input == '' || input == undefined) {
        return true;
    } else {
        return false;
    }
}