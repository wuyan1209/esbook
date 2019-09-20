import os
import random
import smtplib
import uuid
import time
from email.mime.text import MIMEText
from email.header import Header
from django.db import connection
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from esbook.settings import MEDIA_ROOT

# 第三方 SMTP 服务
mail_host = "smtp.126.com"  # 设置服务器
mail_user = "s_wuyan@126.com"  # 用户名
mail_pass = "15893703624wy"  # 客户端授权码
mail_port = 465

sender = 's_wuyan@126.com'  # 发送者邮箱


# 跳转到主页面
def index(request):
    userId = request.session.get("userId")
    if userId:
        return render(request, 'index.html')
    else:
        return redirect("login/")


# 跳转到登录页面
def login(requset):
    return render(requset, "login.html")


# 跳转到注册页面
def register(request):
    return render(request, 'register.html');


# 校验用户名
def valiName(request):
    name = request.POST['name'];  # 用户名
    # 判断用户名是否存在
    cursor = connection.cursor()
    cursor.execute('select user_id from user where user_name=%s', [name])
    userId = cursor.fetchone()
    cursor.close()
    if userId:
        return JsonResponse({'status': 2001, 'message': "用户名已被占用"})
    return JsonResponse({'status': 200, 'message': "ok"})


# 校验手机号
def valiPhone(request):
    phone = request.POST['phone'];
    # 判断用户名是否存在
    cursor = connection.cursor()
    cursor.execute('select user_id from user where phone=%s', [phone])
    userId = cursor.fetchone()
    cursor.close()
    if userId:
        return JsonResponse({'status': 2001, 'message': "手机号已被占用"})
    return JsonResponse({'status': 200, 'message': "ok"})


# 校验邮箱号
def valiEmail(request):
    email = request.POST['email'];
    # 判断用户名是否存在
    cursor = connection.cursor()
    cursor.execute('select user_id from user where email=%s', [email])
    userId = cursor.fetchone()
    cursor.close()
    if userId:
        return JsonResponse({'status': 2001, 'message': "邮箱号已被占用"})
    return JsonResponse({'status': 200, 'message': "ok"})


# 封装一个方法直接传入邮件标题和内容
def postEmail(request):
    # 获取邮箱号
    email=request.POST['email']
    receivers = [email]  # 接收者邮件
    list = " "
    for i in range(4):
        n = random.randint(0, 9)
        s = str(n)
        list += s
    context = '您的验证码是：' + list  # 内容
    title = 'Python SMTP 邮件验证码'  # 标题
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(context, 'plain', 'utf-8')
    message['From'] = Header(sender)  # 发送者
    message['To'] = Header(str(";".join(receivers)))  # 接收者
    message['Subject'] = Header(title)
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        return JsonResponse({'status':200,'message':int(list)})
    except smtplib.SMTPException:
        return JsonResponse({'status':2001,'message':'获取失败，请重新获取'})


# 注册
def Register(request):
    name = request.POST['name'];  # 用户名
    email = request.POST['email'];  # 邮箱号
    phone = request.POST['phone'];  # 手机号
    password = request.POST['password'];  # 密码
    localTime = time.localtime(time.time())  # 获取当前时间
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)  # 格式化当前日期 ‘年-月-日 时：分：秒’
    # 密码加密
    pwd = make_password(password, 'a')
    cursor = connection.cursor()
    # 判断是手机号注册还是邮箱注册
    # 手机注册
    if phone!=' ':
        try:
            cursor.execute("insert into user (user_name, password, phone, cre_date) values (%s,%s,%s,%s)",
                           [name, pwd, phone, formatTime])
            return HttpResponseRedirect("/login/")
        except:
            return HttpResponseRedirect("/register/")
    # 邮箱注册
    else:
        try:
            cursor.execute("insert into user (user_name, password, email, cre_date) values (%s,%s,%s,%s)",
                           [name, pwd, email, formatTime])
            return HttpResponseRedirect("/login/")
        except:
            return HttpResponseRedirect("/register/")


# 登录
def userLogin(request):
    userName = request.POST['userName']
    password = request.POST['password']
    cursor = connection.cursor()
    if userName.find("@") == -1:  # -1代表找不到  0代表找到
        # 手机号登录
        # 判断用户是否存在
        cursor.execute('select user_id,user_name,password,icon from user where phone=' + userName)
        user = cursor.fetchone()
        if user:
            # 判断密码是否正确
            ret = check_password(password, user[2])
            if ret:
                # 用户存session
                request.session['username'] = user[1]
                request.session['userId'] = user[0]
                request.session['icon'] = user[3]
                return HttpResponseRedirect('/index/')  # 跳转到主界面
            else:
                return render(request, 'login.html', {"error": "密码错误"})
        else:
            return render(request, 'login.html', {"error": "用户不存在"})
    else:
        # 邮箱登录
        # 判断用户是否存在
        cursor.execute('select user_id,user_name,password,icon from user where email=%s', [userName])
        user = cursor.fetchone()
        if user:
            # 判断密码是否正确
            ret = check_password(password, user[2])
            if ret:
                # 用户存session
                request.session['username'] = user[1]
                request.session['userId'] = user[0]
                request.session['icon'] = user[3]
                return HttpResponseRedirect('/index/')  # 跳转到主界面
            else:
                return render(request, 'login.html', {"error": "密码错误"})
        else:
            return render(request, 'login.html', {"error": "用户不存在"})


# 退出登录
def logout(request):
    # 清除sessoin
    request.session.clear();
    return HttpResponseRedirect('/login/')  # 跳转到登录页面


# 个人中心
def personal(request):
    return render(request, 'personal.html');


# 上传图片
def uploadImg(request):
    # 获取文件
    f1 = request.FILES['pic']
    # 通过uuid为文件重命名
    name = str(uuid.uuid1()) + "." + f1.name.split('.')[1]
    # 项目里的绝对路径
    fname = os.path.join(MEDIA_ROOT, name)
    # 上传到项目
    with open(fname, 'wb+') as pic:
        for c in f1.chunks():
            pic.write(c)
    # 把头像路径添加到数据库
    cursor = connection.cursor()
    userId = request.session['userId']
    cursor.execute('update user set icon=%s where user_id=%s', [name, userId])
    cursor.close()
    request.session['icon'] = name;
    # 重定向到个人中心
    return HttpResponseRedirect('/personal/')


# 获取个人信息
def getUser(request):
    userId = request.session['userId']
    cursor = connection.cursor()
    cursor.execute('select user_id, password,user_name, email, phone, icon, cre_date from user where user_id=%s', [userId])
    result = cursor.fetchone()
    return JsonResponse({"result": result})


# 查看密码是否正确
def conpwd(request):
    password=request.POST['password']
    userId = request.session['userId']
    cursor = connection.cursor()
    cursor.execute('select password from user where user_id=%s',[userId])
    result = cursor.fetchone()[0]
    # 判断密码是否正确
    ret = check_password(password, result)
    if ret:
        return JsonResponse({"status":200})
    else:
        return JsonResponse({"status":2001,"message":"密码错误"})


#修改密码
def modifyPwd(request):
    npwd = request.POST['npassword']
    userId = request.session['userId']
    # 密码加密
    npwd = make_password(npwd, 'a')
    # 修改
    cursor = connection.cursor()
    try:
        cursor.execute('update user set password=%s where user_id=%s',[npwd,userId])
        return JsonResponse({"status":200,"message":"修改成功"})
    except:
        return JsonResponse({"status":2003,"message":"修改失败"})

# 个人中心的重置密码页面
def resetPassword(request):
    return render(request, 'resetPassword.html');

# 登录的重置密码页面
def resetPwd(request):
    return render(request, 'resetPwd.html');

# 重置密码
def updatePwd(request):
    pwd=request.POST['pwd']
    email = request.POST['email']
    userId = request.session['userId']
    # 密码加密
    pwd = make_password(pwd, 'a')
    # 修改
    cursor = connection.cursor()
    # 查找该用户是否通绑定邮箱
    cursor.execute('select user_id from user where email=%s and user_id=%s',[email,userId])
    user=cursor.fetchone()
    print(user)
    if user:
        try:
            cursor.execute('update user set password=%s where user_id=%s', [pwd, userId])
            return JsonResponse({"status": 200, "message": "修改成功"})
        except:
            return JsonResponse({"status": 2003, "message": "修改失败"})
    else:
        return JsonResponse({"status": 2001, "message": "用户不存在"})


# 绑定邮箱
def bindEmail(request):
    email = request.POST['email']
    userId = request.session['userId']
    # 修改
    cursor = connection.cursor()
    try:
        cursor.execute('update user set email=%s where user_id=%s', [email, userId])
        return JsonResponse({"status": 200, "message": "绑定成功"})
    except:
        return JsonResponse({"status": 2003, "message": "绑定失败"})