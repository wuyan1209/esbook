import docx
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django.contrib.auth.hashers import make_password, check_password
from document.models import User
import time  # 引入time模块
import json  # 引入json模块
import os
from itertools import chain

# 跳转到主页面
from esbook.settings import BASE_DIR


def index(request):
    return render(request, 'index.html')


# 新建docs
def RTFdocs(request):
    saveState = request.GET.get("saveState")
    return render(request, 'RTFdocs.html', {'saveState': saveState})


# 添加协作空间
@transaction.atomic
def addTeam(request):
    if request.is_ajax():
        # 获取空间名
        teamName = request.POST['teamName']
        localTime = time.localtime(time.time())  # 获取当前时间
        formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)  # 格式化当前日期 ‘年-月-日 时：分：秒’
        try:
            # 空间名是唯一的，查询是否在数据库里存在
            cursor = connection.cursor()
            cursor.execute('select team_id from team where team_name=%s', [teamName])
            tid = cursor.fetchone()
            if tid:
                return JsonResponse({'status': 10023, 'message': '协作空间名字已被占用，请换个名字'})
            # 从session里获取当前登录用户
            username = request.session.get('username')
            # 通过用户名获取该用户的id
            userId = User.objects.get(user_name=username).user_id
            # 创建保存点
            save_id = transaction.savepoint()
            # 添加协作空间
            cursor.execute('insert into team(team_name,user_id,date) value(%s,%s,%s)', [teamName, userId, formatTime])
            # 把创建协作空间的人员与协作空间关联到第三张表 team_member表
            cursor.execute('select team_id from team  order by team_id desc limit 1')
            row = cursor.fetchall()
            cursor.execute('insert into team_member(team_id,user_id) value(%s,%s)', [row[0], userId])
            # 把人员与角色绑定
            cursor.execute('select team_mem_id from team_member order by team_mem_id desc limit 1')
            tmid = cursor.fetchall()
            cursor.execute('insert into member_role(team_mem_id,role_id) value(%s,%s)', [tmid[0], 4])
            cursor.close()
            # 成功的话保存
            transaction.savepoint_commit(save_id)
            return JsonResponse({'status': 200, 'message': '添加成功'})
        except:
            # 失败的时候回滚到保存点
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'status': 4001, 'message': '添加失败'})


# 修改协作空间
def editTeam(request):
    if request.is_ajax():
        # 获取原本的空间名和要修改为的空间名
        teamName = request.POST['teamName']
        preTeamName = request.POST['pTeamName']
        # 空间名是唯一的，查询是否在数据库里存在
        try:
            cursor = connection.cursor()
            cursor.execute('select team_id from team where team_name=%s', [teamName])
            tid = cursor.fetchone()
            if tid:
                return JsonResponse({'status': 10023, 'message': '协作空间名字已被占用，请换个名字'})
            cursor.execute('update team set team_name=%s where team_name=%s', [teamName, preTeamName])
            cursor.close()
            # 成功的话
            return JsonResponse({'status': 200, 'message': '修改成功'})
        except:
            return JsonResponse({'status': 4001, 'message': '修改失败'})


# 主页面查询该成员加入的协作空间
def getAllTeam(request):
    if request.is_ajax():
        cursor = connection.cursor()
        # 获取session里存放的username
        username = request.session.get('username')
        cursor.execute('select team.team_id, team_name from team, team_member, user '
                       'where team.team_id = team_member.team_id and team_member.user_id = user.user_id '
                       'and team_state=0 and user.user_name ="' + username + '" ')
        result = cursor.fetchall()
        cursor.close()
        return JsonResponse({"status": 200, "list": result})


# 通过用户名查询用户
def serachUser(request):
    # 获取用户名和协作空间名
    userName = request.POST['userName']
    teamName = request.POST['teamName']
    cursor = connection.cursor()
    # 查询用户是否是该协作空间的协作者
    cursor.execute('select u.user_id from user u,team t,team_member tm ' +
                   'where u.user_id=tm.user_id and tm.team_id=t.team_id and u.user_name="' + userName + '" and t.team_name="' + teamName + '"')
    userId = cursor.fetchone()
    if userId:
        cursor.close()
        return JsonResponse({'status': 1002, 'message': '该用户已经添加过了'})
    else:
        # 查询该用户的信息
        cursor.execute('select user_id,user_name,icon from user where user_name="' + userName + '" ')
        result = cursor.fetchone()
        cursor.close()
        if result:
            return JsonResponse({'status': 200, 'message': result})
        else:
            return JsonResponse({'status': 1002, 'message': '用户不存在'})


# 将成员加入到协作空间并设置角色
@transaction.atomic
def addMember(request):
    # 获取用户名、协作空间名、角色名
    userName = request.POST['userName']
    teamName = request.POST['teamName']
    roleName = request.POST['roleName']
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限添加
    cursor = connection.cursor()
    cursor.execute(
        'select DISTINCT role_name from role r,member_role mr,team_member tm,user u ,team t where r.role_id=mr.role_id '
        'and mr.team_mem_id=tm.team_mem_id and t.team_id=tm.team_id and tm.user_id=u.user_id and u.user_name=%s and t.team_name=%s',
        [username, teamName])
    result = cursor.fetchone()
    if result[0] == '管理员' or result[0] == '超级管理员':
        try:
            # 查询用户id和协作空间id
            cursor.execute('select user_id from user where user_name="' + userName + '"')
            userId = cursor.fetchall()
            cursor.execute('select team_id from team where team_name="' + teamName + '"')
            teamId = cursor.fetchall()
            # 创建保存点
            save_id = transaction.savepoint()
            # 把用户添加到协作空间里
            cursor.execute('insert into team_member(team_id,user_id) value(%s,%s)', [teamId[0], userId[0]])
            # 查询插入的协作空间成员的id
            cursor.execute('select team_mem_id from team_member order by team_mem_id desc limit 1')
            tmid = cursor.fetchall()
            # 通过角色名查询角色id
            cursor.execute('select role_id from role where role_name="' + roleName + '"')
            roleId = cursor.fetchall()
            # 把人员与角色绑定
            cursor.execute('insert into member_role(team_mem_id,role_id) value(%s,%s)', [tmid[0], roleId[0]])
            # 成功的话保存
            status = 200
            message = '添加成功'
            transaction.savepoint_commit(save_id)
        except:
            # 失败的时候回滚到保存点
            status = 4001
            message = '添加失败'
            transaction.savepoint_rollback(save_id)
        return JsonResponse({'status': status, 'message': message})
    else:
        return JsonResponse({'status': 2002, 'message': '抱歉，您没有权限'})


# 保存个人空间的docs
@transaction.atomic
def RTFdocs_save(request):
    doc_content = request.POST.get('doc_content')  # 文档内容
    doc_title = request.POST.get('doc_title')  # 文档标题
    userId = request.session.get("userId")
    localTime = time.localtime(time.time())  # 获取当前时间
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)  # 格式化当前日期 ‘年-月-日 时：分：秒’
    return_param = {}
    sid = transaction.savepoint()
    try:
        # 数据库更新
        cursor = connection.cursor()
        cursor.execute("insert into file(file_name,content,cre_date,type) values(%s,%s,%s,0)",
                       [doc_title, doc_content, formatTime])
        cursor.execute("select file_id from file where file_name = %s", [doc_title])
        file_id = cursor.fetchone()

        cursor.execute("insert into user_file(user_id,file_id) values (%s,%s)", [userId, file_id])
        return_param['saveStatus'] = "success"
        return_param['userId'] = userId
        return_param['fileId'] = file_id[0]
        transaction.savepoint_commit(sid)
    except Exception as e:
        # 数据库更新失败
        return_param['saveStatus'] = "fail"
        transaction.savepoint_rollback(sid)
    return HttpResponse(json.dumps(return_param))


# 保存协作空间的docs
def saveTeamDoc(request):
    doc_content = request.POST.get('doc_content', 0)  # 文档内容
    doc_title = request.POST.get('doc_title', 0)  # 文档标题
    teamId = request.POST.get('teamId')  # 团队ID
    localTime = time.localtime(time.time())  # 获取当前时间
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)  # 格式化当前日期 ‘年-月-日 时：分：秒’
    userId = request.session.get("userId")
    return_param = {}
    sid = transaction.savepoint()
    try:
        # 数据库更新
        cursor = connection.cursor()
        # 向file表中插入文件数据
        cursor.execute("insert into file(file_name,content,cre_date) values(%s,%s,%s)",
                       [doc_title, doc_content, formatTime])
        # 获取文件id
        cursor.execute("select file_id from file where file_name = %s", [doc_title])
        file_id = cursor.fetchone()[0]

        # 获取团队成员id
        cursor.execute("select team_mem_id from team_member where user_id=%s and team_id = %s;", [userId, teamId])
        team_mem_id = cursor.fetchone()
        # 保存团队文件
        cursor.execute("insert into member_file(team_mem_id, file_id) values (%s,%s)", [team_mem_id, file_id])
        return_param['saveStatus'] = "success"
        return_param['fileId'] = file_id
        return_param['teamId'] = teamId
        transaction.savepoint_commit(sid)
    except Exception as e:
        # 数据库更新失败
        return_param['saveStatus'] = "fail"
        transaction.savepoint_rollback(sid)
    return HttpResponse(json.dumps(return_param))


# 判断文档名称是否重复
def docNameExist(request):
    docName = request.POST.get('docsName')  # 获取文档标题
    saveState = request.POST.get('saveState')  # 获取文档状态
    userId = request.session.get('userId')
    teamId = request.POST.get('teamId')  # 获取团队Id
    return_param = {}
    # 从数据库中查询文档标题
    cursor = connection.cursor()
    if saveState == "my_doc":
        # 个人文档的名称是否重复
        cursor.execute('select file_name from file f where f.file_id in'
                       ' (select file_id from user_file where user_id = %s)', [userId])
        fileNamas = cursor.fetchall()
        for fileName in fileNamas:
            if str(fileName[0]) == docName:
                return_param['Exist'] = "YES"
                break
            else:
                return_param['Exist'] = "No"
    else:
        # 团队文档的名称是否重复
        cursor.execute("select file_name from file f, member_file mf "
                       "where f.file_id = mf.file_id and mf.team_mem_id in "
                       "(select team_mem_id from team_member where team_id = %s)", [teamId])
        fileNamas = cursor.fetchall()
        for fileName in fileNamas:
            if str(fileName[0]) == docName:
                return_param['Exist'] = "YES"
                break
            else:
                return_param['Exist'] = "No"
    return HttpResponse(json.dumps(return_param))


# 查询文件
def fileList(request):
    page = request.POST['page']
    # 获取session里存放的username
    username = request.session.get('username')
    # 每页显示条数
    pageSize = 10
    cursor = connection.cursor()
    cursor.execute('select count(*) '
                   'from user u,file f,user_file uf '
                   'where u.user_id=uf.user_id and f.file_state = 0 and f.file_id=uf.file_id and u.user_name ="' + username + '"')
    count = cursor.fetchone()[0]  # 总条数
    totalPage = count / pageSize  # 总页数
    if count != 0:
        if count % pageSize != 0:
            totalPage = totalPage + 1
            # 当页数大于总页数，直接返回
        if int(page) > totalPage:
            return JsonResponse({"status": 2002})
        offset = (int(page) - 1) * pageSize  # 计算sql需要的起始索引
        cursor.execute('select f.file_name,u.user_name,f.cre_date,u.user_id,f.file_id,f.type '
                       'from user u,file f,user_file uf '
                       'where u.user_id=uf.user_id and f.file_state = 0 and f.file_id=uf.file_id and u.user_name ="' + username + '"'
                                                                                                                                  ' order by f.cre_date desc limit %s,%s',
                       [offset, pageSize])
        list = cursor.fetchall()
        cursor.close()
        return JsonResponse(
            {'status': 200, "page": int(page), "pageSize": pageSize, "totalPage": totalPage, "list": list})
    return JsonResponse({'status': 2001, 'message': '暂无数据'})


# 修改doc文档
def docsModify(request):
    file_name = request.GET.get("file_name")  # 获取文件名称
    fileId = request.GET.get("fileId")  # 获取文件id
    saveState = request.GET.get("saveState")  # 获取文件状态
    user_id = request.GET.get("user_id")  # 获取文件状态
    roleName = request.GET.get("roleName")  # 获取该用户对此文件的角色

    cursor = connection.cursor()
    cursor.execute('select content from file f '
                   'where f.file_id = %s',
                   [fileId])
    doc_content = cursor.fetchone()[0]
    request.session["file_name"] = file_name
    request.session["doc_content"] = doc_content
    request.session["file_id"] = fileId
    request.session["roleName"] = roleName
    # return HttpResponse(json.dumps({'data': 'success'}))
    return render(request, "modify_RTFdocs.html", {"saveState": saveState})


# 修改页面
def modifyRTFdocs(request):
    # file_name = request.GET.get("file_name")
    # doc_content = request.GET.get("doc_content")
    saveState = request.GET.get("saveState")
    return render(request, "modify_RTFdocs.html", {"saveState": saveState})


# 修改文档
@transaction.atomic
def ajax_modify_RTFdoc(request):
    doc_content = request.POST.get('doc_content')  # 文档内容
    now_doc_title = request.POST.get('now_doc_title')  # 当前文档标题
    fileId = request.POST.get('fileId')  # 文件ID

    localTime = time.localtime(time.time())  # 获取当前时间
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)  # 格式化当前日期 ‘年-月-日 时：分：秒’
    return_param = {}
    sid = transaction.savepoint()
    cursor = connection.cursor()
    try:
        # 数据库更新
        cursor.execute(
            "update file f set f.file_name = %s , f.content = %s, f.cre_date = %s "
            "where f.file_id = %s",
            [now_doc_title, doc_content, formatTime, fileId]
        )
        return_param['saveStatus'] = "success"

        transaction.savepoint_commit(sid)
    except Exception as e:
        # 数据库更新失败
        return_param['saveStatus'] = "fail"
        transaction.savepoint_rollback(sid)
    return HttpResponse(json.dumps(return_param))


# 查询协作空间普通成员
def serachTeamUser(request):
    # 协作空间名
    teamName = request.POST['teamName']
    cursor = connection.cursor()
    # 查询协作空间普通成员
    cursor.execute(
        'select mr.mem_role_id,u.user_name,u.icon,r.role_name from user u,team t,team_member tm,member_role mr,role r ' +
        'where t.team_id=tm.team_id and tm.user_id=u.user_id and tm.team_mem_id=mr.team_mem_id ' +
        'and mr.role_id=r.role_id and t.team_name="' + teamName + '"and r.role_id in(1,2)')
    result = cursor.fetchall()
    cursor.close()
    return JsonResponse({'status': 200, 'message': result})


# 查询协作空间管理员和超管
def serachTeamAdmin(request):
    # 协作空间名
    teamName = request.POST['teamName']
    cursor = connection.cursor()
    # 查询协作空间普通成员
    cursor.execute(
        'select mr.mem_role_id,u.user_name,u.icon,r.role_name from user u,team t,team_member tm,member_role mr,role r ' +
        'where t.team_id=tm.team_id and tm.user_id=u.user_id and tm.team_mem_id=mr.team_mem_id ' +
        'and mr.role_id=r.role_id and t.team_name="' + teamName + '"and r.role_id in(3,4)')
    result = cursor.fetchall()
    cursor.close()
    return JsonResponse({'status': 200, 'message': result})


# 修改协作者的角色
@transaction.atomic
def editMemberRole(request):
    roleName = request.POST.get('roleName')  # 角色名
    memRoleId = request.POST.get('memRoleId')  # 成员角色id
    teamName = request.POST['teamName']
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute(
        'select DISTINCT role_name from role r,member_role mr,team_member tm,user u ,team t where r.role_id=mr.role_id '
        'and mr.team_mem_id=tm.team_mem_id and t.team_id=tm.team_id and tm.user_id=u.user_id and u.user_name=%s and t.team_name=%s',
        [username, teamName])
    result = cursor.fetchone()
    if result[0] == '管理员' or result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 修改角色
            cursor.execute(
                'update member_role set role_id=(select role_id from role where role_name="' + roleName + '") where mem_role_id=' + memRoleId)
            cursor.close()
            # 成功的话保存
            status = 200
            message = '修改成功'
            transaction.savepoint_commit(saveId)
        except:
            # 失败的时候回滚到保存点
            status = 4001
            message = '修改失败'
            transaction.savepoint_rollback(saveId)
        return JsonResponse({'status': status, 'message': message})
    else:
        return JsonResponse({'status': 2002, 'message': '抱歉，您没有权限'})


# 修改协作者为超管
@transaction.atomic
def editAdminRole(request):
    roleName = request.POST.get('roleName')  # 角色名
    memRoleId = request.POST.get('memRoleId')  # 成员角色id
    teamName = request.POST.get("teamName")
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute(
        'select DISTINCT role_name from role r,member_role mr,team_member tm,user u ,team t where r.role_id=mr.role_id '
        'and mr.team_mem_id=tm.team_mem_id and t.team_id=tm.team_id and tm.user_id=u.user_id and u.user_name=%s and t.team_name=%s',
        [username, teamName])
    result = cursor.fetchone()
    if result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 修改角色
            cursor.execute(
                'update member_role set role_id=(select role_id from role where role_name="' + roleName + '") where mem_role_id=' + memRoleId)
            cursor.close()
            # 成功的话保存
            status = 200
            message = '修改成功'
            transaction.savepoint_commit(saveId)
        except:
            # 失败的时候回滚到保存点
            status = 4001
            message = '修改失败'
            transaction.savepoint_rollback(saveId)
        return JsonResponse({'status': status, 'message': message})
    else:
        return JsonResponse({'status': 2002, 'message': '抱歉，您没有权限'})


# 移除协作者的角色
@transaction.atomic
def delMemberRole(request):
    memRoleId = request.POST.get('memRoleId')  # 成员角色id
    teamName = request.POST['teamName']
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute(
        'select DISTINCT role_name from role r,member_role mr,team_member tm,user u ,team t where r.role_id=mr.role_id '
        'and mr.team_mem_id=tm.team_mem_id and t.team_id=tm.team_id and tm.user_id=u.user_id and u.user_name=%s and t.team_name=%s',
        [username, teamName])
    result = cursor.fetchone()
    if result[0] == '管理员' or result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 移除角色
            cursor.execute(
                'delete tm,mr from team_member tm,member_role mr where tm.team_mem_id=mr.team_mem_id and mr.mem_role_id=' + memRoleId)
            cursor.close()
            # 成功的话保存
            status = 200
            message = '移除成功'
            transaction.savepoint_commit(saveId)
        except:
            # 失败的时候回滚到保存点
            status = 4001
            message = '移除失败'
            transaction.savepoint_rollback(saveId)
        return JsonResponse({'status': status, 'message': message})
    else:
        return JsonResponse({'status': 2002, 'message': '抱歉，您没有权限'})


# 移除协作者管理员角色，改为可编辑
@transaction.atomic
def delAdminRole(request):
    memRoleId = request.POST.get('memRoleId')  # 成员角色id
    teamName = request.POST['teamName']
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute(
        'select DISTINCT role_name from role r,member_role mr,team_member tm,user u ,team t where r.role_id=mr.role_id '
        'and mr.team_mem_id=tm.team_mem_id and t.team_id=tm.team_id and tm.user_id=u.user_id and u.user_name=%s and t.team_name=%s',
        [username, teamName])
    result = cursor.fetchone()
    if result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 角色修改为可编辑
            cursor.execute(
                'update member_role set role_id=(select role_id from role where role_name="可编辑") where mem_role_id=' + memRoleId)
            cursor.close()
            # 成功的话保存
            status = 200
            message = '移除成功'
            transaction.savepoint_commit(saveId)
        except:
            # 失败的时候回滚到保存点
            status = 4001
            message = '移除失败'
            transaction.savepoint_rollback(saveId)
        return JsonResponse({'status': status, 'message': message})
    else:
        return JsonResponse({'status': 2002, 'message': '抱歉，您没有权限'})


# 把协作空间移到回收站
def delTeam(request):
    # 协作空间的id
    teamId = request.POST.get("teamId")
    try:
        cursor = connection.cursor()
        cursor.execute('update team set team_state=1 where team_id=' + teamId)
        cursor.close()
        # 成功的话保存
        status = 200
        message = '删除成功'
    except:
        # 失败
        status = 4001
        message = '删除失败'
    return JsonResponse({'status': status, 'message': message})


# 团队文件
def teamfile(request):
    teamname = request.POST.get("teamName")
    page = request.POST['page']
    # 获取session的name
    username = request.session['username']
    # 每页显示条数
    pageSize = 10
    cursor = connection.cursor()
    # 用户在此协作空间的角色
    cursor.execute(
        'select r.role_name from user u,team t,team_member tm,member_role mr,role r where u.user_id=tm.user_id '
        ' and tm.team_id=t.team_id and tm.team_mem_id=mr.team_mem_id and mr.role_id=r.role_id '
        ' and u.user_name=%s and t.team_name=%s', [username, teamname])
    roleName = cursor.fetchone()[0]
    # 总条数
    cursor.execute('select count(*) '
                   ' from team t,team_member tm,member_file mf,file f ,user u where f.file_state = 0 and t.team_id=tm.team_id'
                   ' and tm.user_id=u.user_id and tm.team_mem_id=mf.team_mem_id and mf.file_id=f.file_id '
                   ' and  t.team_name ="' + teamname + '" ')
    count = cursor.fetchone()[0]
    totalPage = count / pageSize  # 总页数
    if count != 0:
        if count % pageSize != 0:
            totalPage = totalPage + 1
            # 当页数大于总页数，直接返回
        if int(page) > totalPage:
            return JsonResponse({"status": 2002})
        offset = (int(page) - 1) * pageSize  # 计算sql需要的起始索引
        cursor.execute(
            'select t.team_id,t.team_name,u.user_id,u.user_name,mf.file_id,f.file_name,f.cre_date,f.file_id,f.type '
            ' from team t,team_member tm,member_file mf,file f ,user u where f.file_state = 0 and t.team_id=tm.team_id'
            ' and tm.user_id=u.user_id and tm.team_mem_id=mf.team_mem_id and mf.file_id=f.file_id '
            ' and  t.team_name ="' + teamname + '"order by f.cre_date desc limit %s,%s', [offset, pageSize])
        list = cursor.fetchall()
        cursor.close()
        return JsonResponse(
            {'status': 200, "page": int(page), "pageSize": pageSize, "totalPage": totalPage, "list": list,
             "roleName": roleName})
    return JsonResponse({'status': 2001, 'message': '暂无数据'})


# 登录页面
def login(requset):
    return render(requset, "login.html")


# 我的回收站
def myBin(request):
    page = request.POST['page']
    # 获取session的用户
    username = request.session['username']
    # 每页显示条数
    pageSize = 10
    cursor = connection.cursor()
    cursor.execute('select count(*) from( '
                   '(select distinct t.team_name, t.date time,t.team_id,t.what from user u, team t, team_member tm'
                   ' where u.user_id=tm.user_id and t.team_id=tm.team_id and t.team_state=1 and u.user_name="' + username + '")'
                                                                                                                            ' UNION'
                                                                                                                            ' (select f.file_name, f.cre_date time,f.file_id,f.type from file f, user u, user_file uf'
                                                                                                                            ' where f.file_id=uf.file_id and u.user_id=uf.user_id'
                                                                                                                            ' and f.file_state=1 and u.user_name="' + username + '")'
                                                                                                                                                                                 ' UNION'
                                                                                                                                                                                 ' (select f.file_name, f.cre_date time,f.file_id,f.type from user u,team_member tm,member_file mf,file f where u.user_id=tm.user_id and tm.team_mem_id=mf.team_mem_id and mf.file_id=f.file_id'
                                                                                                                                                                                 ' and f.file_state=1 and u.user_name="' + username + '")'
                                                                                                                                                                                                                                      ' )t ORDER BY time DESC')
    count = cursor.fetchone()[0]  # 总条数
    totalPage = count / pageSize  # 总页数
    if count != 0:
        if count % pageSize != 0:
            totalPage = totalPage + 1
            # 当页数大于总页数，直接返回
        if int(page) > totalPage:
            return JsonResponse({"status": 2002})
        offset = (int(page) - 1) * pageSize  # 计算sql需要的起始索引
        # 获取状态为1的属于此用户的文件和团队
        cursor.execute('select * from( '
                       '(select distinct t.team_name, t.date time,t.team_id,t.what from user u, team t, team_member tm'
                       ' where u.user_id=tm.user_id and t.team_id=tm.team_id and t.team_state=1 and u.user_name="' + username + '")'
                                                                                                                                ' UNION'
                                                                                                                                ' (select f.file_name, f.cre_date time,f.file_id,f.type from file f, user u, user_file uf'
                                                                                                                                ' where f.file_id=uf.file_id and u.user_id=uf.user_id'
                                                                                                                                ' and f.file_state=1 and u.user_name="' + username + '")'
                                                                                                                                                                                     ' UNION'
                                                                                                                                                                                     ' (select f.file_name, f.cre_date time,f.file_id,f.type from user u,team_member tm,member_file mf,file f where u.user_id=tm.user_id and tm.team_mem_id=mf.team_mem_id and mf.file_id=f.file_id'
                                                                                                                                                                                     ' and f.file_state=1 and u.user_name="' + username + '")'
                                                                                                                                                                                                                                          ' )t ORDER BY time DESC limit %s,%s',
                       [offset, pageSize])
        result = cursor.fetchall()
        cursor.close()
        return JsonResponse(
            {'status': 200, 'message': result, "page": int(page), "pageSize": pageSize, "totalPage": totalPage})
    return JsonResponse({'status': 2001, 'message': '暂无数据'})


# 回收站恢复文件
def restore(request):
    id = request.POST['id']
    what = request.POST['what']
    cursor = connection.cursor()
    # 判断该文件是文档还是协作空间
    if what == '协作空间':
        row = cursor.execute('update team set team_state=0 where team_id=' + id)
    else:
        row = cursor.execute('update file set file_state=0 where file_id=' + id)
    cursor.close()
    if row == 1:
        return JsonResponse({'status': 200, 'message': '已成功恢复文件至协作空间'})
    else:
        return JsonResponse({'status': 4001, 'message': '出现错误'})


# 回收站彻底删除文件
def deleteAll(request):
    id = request.POST['id']
    what = request.POST['what']
    cursor = connection.cursor()
    try:
        # 判断该文件是文档还是协作空间
        if what == '协作空间':
            # 判断该协作空间是否有文件
            cursor.execute(
                'select mf.file_id from file f,member_file mf,member_role mr,team_member tm,team t where f.file_id=mf.file_id '
                ' and mf.team_mem_id=tm.team_mem_id and mr.team_mem_id=tm.team_mem_id and tm.team_id=t.team_id and t.team_id=' + id)
            fileId = cursor.fetchall()
            # 有文件
            if fileId:
                # 判断文件是否有版本
                cursor.execute(
                    'select me.edi_id from edition e,member_edition me,file f,member_file mf,member_role mr,team_member tm,team t where f.file_id=mf.file_id '
                    ' and mf.team_mem_id=tm.team_mem_id and mr.team_mem_id=tm.team_mem_id and mf.mem_file_id=me.mem_file_id '
                    ' and me.edi_id=e.edi_id and tm.team_id=t.team_id and t.team_id=' + id)
                ediId = cursor.fetchall()
                print(ediId)
                # 有版本
                if ediId:
                    cursor.execute(
                        'delete e,me,mf,f,mr,tm,t from edition e,member_edition me,file f,member_file mf,member_role mr,team_member tm,team t where f.file_id=mf.file_id and mf.team_mem_id=tm.team_mem_id and mr.team_mem_id=tm.team_mem_id and mf.mem_file_id=me.mem_file_id and me.edi_id=e.edi_id and tm.team_id=t.team_id and t.team_id=' + id)
                # 无版本
                else:
                    cursor.execute(
                        'delete mf,f,mr,tm,t from file f,member_file mf,member_role mr,team_member tm,team t where f.file_id=mf.file_id and mf.team_mem_id=tm.team_mem_id and mr.team_mem_id=tm.team_mem_id and tm.team_id=t.team_id and t.team_id=' + id)
            # 无文件
            else:
                cursor.execute(
                    'delete mr,tm,t from member_role mr,team_member tm,team t WHERE mr.team_mem_id=tm.team_mem_id and tm.team_id=t.team_id and t.team_id=' + id)
        else:
            # 判断文件是私有文件还是团队文件
            cursor.execute(
                'select mf.mem_file_id from member_file mf,file f where mf.file_id=f.file_id and f.file_id=' + id)
            result = cursor.fetchall()
            # 团队文件
            if result:
                # 判断文件是否有版本
                cursor.execute(
                    'select me.edi_id from edition e,member_edition me,member_file mf,file f where mf.file_id=f.file_id '
                    'and mf.mem_file_id=me.mem_file_id and me.edi_id=e.edi_id and f.file_id=' + id)
                ediId = cursor.fetchall()
                # 有版本
                if ediId:
                    cursor.execute(
                        'delete e,me,mf,f from edition e,member_edition me,member_file mf,file f where mf.file_id=f.file_id and mf.mem_file_id=me.mem_file_id and me.edi_id=e.edi_id and f.file_id=' + id)
                # 无版本，只删除文件
                else:
                    cursor.execute(
                        'delete mf,f from member_file mf,file f where mf.file_id=f.file_id and f.file_id=' + id)
            # 私有文件
            else:
                # 判断文件是否有版本
                cursor.execute(
                    'select ue.edi_id from user_file uf,file f,user_edition ue,edition e where uf.file_id=f.file_id '
                    ' and uf.user_file_id=ue.user_file_id and ue.edi_id=e.edi_id and f.file_id=' + id)
                ediId = cursor.fetchall()
                # 有版本
                if ediId:
                    cursor.execute(
                        'delete e,ue,uf,f from edition e,user_edition ue,user_file uf,file f where uf.file_id=f.file_id and uf.user_file_id=ue.user_file_id and ue.edi_id=e.edi_id and f.file_id=' + id)
                # 无版本，只删除文件
                else:
                    cursor.execute(
                        'delete uf,f from user_file uf,file f where uf.file_id=f.file_id and f.file_id=' + id)
        return JsonResponse({'status': 200, 'message': '删除成功'})
    except:
        return JsonResponse({'status': 4004, 'message': '删除失败'})


# 搜索文件
def searchFile(request):
    cursor = connection.cursor()
    searchCondition = request.POST.get("searchCondition")  # 获取查询条件
    searchedFiles = []
    files = {}
    # 获取username
    username = request.session['username']
    # 用户加入的团队的文件
    userId = request.session["userId"]
    cursor.execute("select team_id from team_member where user_id = %s", [userId])
    teamId = cursor.fetchall()
    teamId = list(chain.from_iterable(teamId))
    cursor.execute("select team_mem_id from team_member where team_id in %s", [teamId])
    team_mem_id = cursor.fetchall()
    cursor.execute(
        "select f.file_id from member_file mf, file f where mf.file_id = f.file_id and mf.team_mem_id in %s and f.file_state = 0",
        [list(chain.from_iterable(team_mem_id))])
    myFileIds = cursor.fetchall()
    myFileIds = list(chain.from_iterable(myFileIds))
    # 用户自己的文件
    cursor.execute("select file_id from user_file where user_id = %s", [userId])
    fileIds = cursor.fetchall()
    myFileIds.extend(list(chain.from_iterable(fileIds)))
    # 查文件
    cursor.execute(
        "select file_id from file where file_name like '%" + searchCondition + "%'")

    selFileIds = cursor.fetchall()
    for fileId in selFileIds:
        if fileId[0] in myFileIds:
            # 根据查询到的fileID来获取file的详细数据
            cursor.execute(
                "select file_name,content,type,cre_date,file_id from file where file_id = %s and file_state = %s",
                [fileId[0], 0])
            searchList = cursor.fetchone()
            if searchList:
                files['file_name'] = searchList[0]
                files['content'] = searchList[1]
                files['type'] = searchList[2]
                files['cre_date'] = searchList[3].strftime("%Y-%m-%d %H:%M:%S")
                files['file_id'] = searchList[4]
                searchedFiles.append(files.copy())
    return HttpResponse(json.dumps(searchedFiles))


# 打开搜索到的文件
def serachRTFdoc(request):
    file_id = request.GET.get("file_id")
    cursor = connection.cursor()
    cursor.execute("select file_id, file_name, content from file where file_id = %s", [file_id])
    fileCodition = cursor.fetchone()
    cursor.execute(
        "select tm.team_id from team_member tm "
        "where tm.team_mem_id = (select team_mem_id from member_file where file_id = %s)", [fileCodition[0]])
    teamId = cursor.fetchone()
    if teamId:
        saveState = teamId[0]
    else:
        saveState = "my_doc"
    request.session["file_id"] = fileCodition[0]
    request.session["file_name"] = fileCodition[1]
    request.session["doc_content"] = fileCodition[2]
    return render(request, "modify_RTFdocs.html", {'saveState': saveState})


# 判断版本内容是否重复
def editionExits(request):
    content = request.POST.get('content')
    return_param = {}
    cursor = connection.cursor()
    # 获取数据库中版本表的content
    cursor.execute("select content from edition ")
    contents = cursor.fetchall()
    # 判断内容是否相同
    for cont in contents:
        if cont[0] == content:
            return_param['Exist'] = "YES"
            break
        else:
            return_param['Exist'] = "No"
    return HttpResponse(json.dumps(return_param))


# 保存个人文件版本
@transaction.atomic
def saveEdition(request):
    # 获取用户名,版本内容,获取文件名称
    username = request.session.get('username')
    content = request.POST.get('content')
    edi_name = request.POST.get('filename')
    # 获取当前时间
    localTime = time.localtime(time.time())
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
    sid = transaction.savepoint()
    try:
        cursor = connection.cursor()
        # 获取用户名、id
        cursor.execute('select user_id from user where user_name="' + username + '"')
        userid = cursor.fetchone()
        cursor.execute("select file_id from file where file_name = %s", [edi_name])
        fileId = cursor.fetchone()
        # 保存版本
        cursor.execute('insert into edition (save_date,content,edi_name) values(%s, %s, %s)',
                       [formatTime, content, edi_name])
        cursor.execute('select edi_id from edition order by edi_id desc limit 1')
        edi_id = cursor.fetchone()
        # 获取个人文件表id
        cursor.execute('select user_file_id from user_file where file_id=%s', [fileId])
        userfileid = cursor.fetchone()
        # user_edition
        cursor.execute('insert into user_edition (user_file_id,edi_id) values(% s, % s)', [userfileid, edi_id])  # 2 6 2
        cursor.close()
        # 事务提交
        transaction.savepoint_commit(sid)
        status = 200
        message = '个人版本保存成功'
    except Exception as e:
        status = 2001
        message = '个人版本保存失败'
        transaction.savepoint_rollback(sid)
    return JsonResponse({'status': 200, "message": message})


# 查看个人版本
def getuseredition(request):
    cursor = connection.cursor()
    # 获取用户名
    username = request.session.get('username')
    # 获取文件名称、id、内容
    filename = request.POST.get('filename')
    cursor.execute('select file_id from file where file_name="' + filename + '"')
    fileid = cursor.fetchone()
    cursor.execute(
        'select  u.user_name,f.file_name,e.save_date,e.content,e.edi_id,e.edi_name from user u,file f,user_edition ue,user_file uf,edition e '
        'where ue.edi_id=e.edi_id and ue.user_file_id=uf.user_file_id and uf.user_id=u.user_id and uf.file_id=f.file_id '
        'and u.user_name = %s and f.file_id = %s and e.edi_state=0 order by e.save_date desc', [username, fileid])
    list = cursor.fetchall()
    cursor.close()
    return JsonResponse({'status': 200, "list": list})


# 保存团队文件版本
@transaction.atomic
def saveTeamEdition(request):
    # 获取成员名、版本内容、文件名
    member = request.session.get('username')
    content = request.POST.get('content')
    fileId = request.POST.get('fileId')
    # 获取当前时间
    localTime = time.localtime(time.time())
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
    sid = transaction.savepoint()
    try:
        cursor = connection.cursor()
        # 获取userid和fileid
        cursor.execute('select user_id from user where user_name="' + member + '"')
        userid = cursor.fetchone()

        # 保存版本
        cursor.execute('insert into edition (save_date,content) values(% s, % s)', [formatTime, content])
        cursor.execute('select edi_id from edition order by edi_id desc limit 1')
        edi_id = cursor.fetchone()
        # 获取团队文件表id
        cursor.execute('select mem_file_id from member_file where file_id=%s', [fileId])
        memfileid = cursor.fetchone()
        # member_edition
        cursor.execute('insert into member_edition (mem_file_id,edi_id) values(% s, % s)', [memfileid, edi_id])
        cursor.close()
        # 事务提交
        status = 200
        message = '团队版本保存成功'
        transaction.savepoint_commit(sid)
    except Exception as e:
        status = 2001
        message = '团队版本保存失败'
        transaction.savepoint_rollback(sid)
        transaction.savepoint_rollback(sid)
    return JsonResponse({'status': 200, "message": message})


# 查看团队版本
def getTeamEdition(request):
    cursor = connection.cursor()
    # 获取空间名、文件名、id、内容
    teamid = request.POST.get('teamid')
    cursor.execute('select team_name from team where team_id="' + teamid + '"')
    teamname = cursor.fetchone()
    fileId = request.POST.get('fileId')
    cursor.execute(
        'select t.team_name,u.user_name,f.file_name,e.save_date,e.content,e.edi_id '
        'from team t,team_member tm,member_file mf,member_edition me,user u ,file f,edition e '
        'where t.team_id=tm.team_id and tm.user_id=u.user_id and tm.team_mem_id=mf.team_mem_id and  mf.file_id=f.file_id and mf.mem_file_id=me.mem_file_id and me.edi_id=e.edi_id '
        'and t.team_name = %s and f.file_id = %s and e.edi_state=0 order by e.save_date desc', [teamname, fileId])
    list = cursor.fetchall()
    cursor.close()
    return JsonResponse({'status': 200, "list": list})


# 跳转到注册页面
def register(request):
    return render(request, 'register.html');


# 注册
def registerUser(request):
    userName = request.POST['userName'];
    phone = request.POST['phone'];
    password = request.POST['password'];
    email = request.POST['email'];
    code = request.POST['code'];
    print(userName + " " + phone + " " + password + " " + email + " " + code)
    return render(request, 'register.html');


# 删除文件
def delFiles(request):
    file_id = request.POST.get("file_id")
    cursor = connection.cursor()
    return_param = {}
    try:
        cursor.execute("update file set file_state = 1 where file_id = %s", [file_id])
        return_param["flag"] = "success"
    except Exception as e:
        return_param["flag"] = "fail"
    return HttpResponse(json.dumps(return_param))


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
    if phone:
        try:
            cursor.execute("insert into user (user_name, password, phone, cre_date) values (%s,%s,%s,%s)",
                           [name, pwd, phone, formatTime])
            status = 200
            message = "ok"
        except:
            status = 4001
            message = "注册失败"
        if status == 200:
            return HttpResponseRedirect("/login/")
        else:
            return JsonResponse({'status': status, 'message': message})
    # 邮箱注册
    else:
        try:
            cursor.execute("insert into user (user_name, password, email, cre_date) values (%s,%s,%s,%s)",
                           [name, pwd, email, formatTime])
            status = 200
            message = "ok"
        except:
            status = 4001
            message = "注册失败"
        if status == 200:
            return HttpResponseRedirect("/login/")
        else:
            return JsonResponse({'status': status, 'message': message})


# 登录
def userLogin(request):
    userName = request.POST['userName']
    password = request.POST['password']
    cursor = connection.cursor()
    if userName.find("@") == -1:  # -1代表找不到  0代表找到
        # 手机号登录
        # 判断用户是否存在
        cursor.execute('select user_id,user_name,password from user where phone=' + userName)
        user = cursor.fetchone()
        if user:
            # 判断密码是否正确
            ret = check_password(password, user[2])
            if ret:
                # 用户存session
                request.session['username'] = user[1]
                request.session['userId'] = user[0]
                return HttpResponseRedirect('/index/')  # 跳转到主界面
            else:
                return render(request, 'login.html', {"error": "密码错误"})
        else:
            return render(request, 'login.html', {"error": "用户不存在"})
    else:
        # 邮箱登录
        # 判断用户是否存在
        cursor.execute('select user_id,user_name,password from user where email=%s', [userName])
        user = cursor.fetchone()
        if user:
            # 判断密码是否正确
            ret = check_password(password, user[2])
            if ret:
                # 用户存session
                request.session['username'] = user[1]
                request.session['userId'] = user[0]
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


# 将本地文件写到项目中
def handle_uploaded_file(file_obj, ext):
    name = os.path.splitext(file_obj.name)[0]
    filename = "%s%s" % (name, ext)
    localurl = "static\\pic\\"
    file_path = os.path.join(BASE_DIR, localurl, filename)
    print(file_path)
    with open(file_path, 'wb+') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)


# 获取文档中的内容
def getcontent(file_path):
    # 获取文档对象
    file = docx.Document(file_path)
    # 输出每一段的内容
    content = ""
    for para in file.paragraphs:
        doc_test = para.text
        styles = para.style.name
        fonts = para.runs
        if styles == 'Heading 1':  # 一级标题
            content += "<h1>" + doc_test + "</h1>"
        elif styles == 'Heading 2':  # 二级标题
            content += "<h2>" + doc_test + "</h2>"
        elif styles == 'Heading 3':  # 3级标题
            content += "<h3>" + doc_test + "</h3>"
        elif styles == 'Heading 4':  # 4级标题
            content += "<h4>" + doc_test + "</h4>"
        elif styles == 'Heading 5':  # 5级标题
            content += "<h5>" + doc_test + "</h5>"
        elif styles == 'Heading 6':  # 6级标题
            content += "<h6>" + doc_test + "</h6>"
        if styles == 'Normal':  # 正常的纯文本
            for f in fonts:
                if (f.bold):  # 加粗
                    content += "<p><strong>" + doc_test + "</strong></p>"
                if (f.italic):  # 斜体
                    content += "<p><i>" + doc_test + "</i></p>"
                if (f.underline):  # 下划线
                    content += "<p><u>" + doc_test + "</u></p>"
                if (f.bold==None and f.italic==None and f.underline==None):  # 没有字体样式
                # if (f.bold==False and f.italic==False and f.underline==False):  # 没有字体样式
                    content += "<p>" + doc_test + "</p>"
        if doc_test == "":
            content += "<p></p>"

    return content


# 个人文件上传
@transaction.atomic
def user_upload_file(request):
    userid = request.session.get("userId")
    # fileobj=request.POST.get('fileobj')
    # print(fileobj)
    # filename=fileobj.name
    # print(filename)
    # name = fileobj.name.split('.')[0]
    # print(filename)
    if request.method == "POST":
        files = request.FILES
        if len(files) == 0:
            message = '没有文件上传，请重新上传'
            return JsonResponse({'message': message})
        for file_key in files:
            file_obj = files[file_key]
            ext = os.path.splitext(file_obj.name)[1]
            name = os.path.splitext(file_obj.name)[0]
            # 调用方法
            handle_uploaded_file(file_obj, ext)
            filename = "%s%s" % (name, ext)
            localurl = "static\\pic\\"
            file_path = os.path.join(BASE_DIR, localurl, filename)
            # 获取当前时间
            localTime = time.localtime(time.time())
            formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
            # 调用方法
            content = getcontent(file_path)
            sid = transaction.savepoint()
            try:
                # 在数据库中存储路径
                cursor = connection.cursor()
                cursor.execute('insert into file(file_name,content,url,cre_date) values(%s,%s,%s,%s)',
                               [name, content, file_path, formatTime])
                cursor.execute("select file_id from file where file_name = %s order by file_id desc limit 1", [name])
                file_id = cursor.fetchone()
                cursor.execute("insert into user_file(user_id,file_id) values (%s,%s)", [userid, file_id])
                cursor.close()
                status = 200
                message = "文件上传成功"
                transaction.savepoint_commit(sid)
                return redirect("/index/")
            except Exception as e:
                # 数据库更新失败
                status = 2001
                message = "文件上传失败"
                transaction.savepoint_rollback(sid)
                return JsonResponse({'status': status, 'message': message})


# 团队文件上传
@transaction.atomic
def team_upload_file(request):
    userid = request.session.get("userId")
    teamID = request.GET.get("saveState")
    if request.method == "POST":
        files = request.FILES
        if len(files) == 0:
            message = '没有文件上传，请重新上传'
            return JsonResponse({'message': message})
        for file_key in files:
            file_obj = files[file_key]
            ext = os.path.splitext(file_obj.name)[1]
            name = os.path.splitext(file_obj.name)[0]
            # 调用方法
            handle_uploaded_file(file_obj, ext)
            filename = "%s%s" % (name, ext)
            localurl = "static\\pic\\"
            file_path = os.path.join(BASE_DIR, localurl, filename)
            # 获取当前时间
            localTime = time.localtime(time.time())
            formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
            # 调用方法
            content = getcontent(file_path)
            sid = transaction.savepoint()
            try:
                # 在数据库中存储路径
                cursor = connection.cursor()
                # 向file表中插入文件数据
                cursor.execute("insert into file(file_name,content,url,cre_date) values(%s,%s,%s,%s)",
                               [name, content, file_path, formatTime])
                # 获取文件id
                cursor.execute("select file_id from file where file_name = %s order by file_id desc limit 1", [name])
                file_id = cursor.fetchone()
                # 获取团队成员id
                cursor.execute("select team_mem_id from team_member where user_id=%s and team_id = %s;",
                               [userid, teamID])
                team_mem_id = cursor.fetchone()
                # 保存团队文件
                cursor.execute("insert into member_file(team_mem_id, file_id) values (%s,%s)",
                               [team_mem_id, file_id])
                cursor.close()
                status = 200
                message = "文件上传成功"
                transaction.savepoint_commit(sid)
                return redirect("/index/")
            except Exception as e:
                # 数据库更新失败
                status = 2001
                message = "文件上传失败"
                transaction.savepoint_rollback(sid)
                return JsonResponse({'status': status, 'message': message})


# 判断导入的文件名是否重复
@transaction.atomic
def uploadexist(request):
    name = request.POST.get('filename')
    userid = request.session.get("userId")
    saveState = request.POST.get('saveState')  # 获取文档状态
    teamId = request.POST.get('teamId')  # 获取团队Id
    filename = name.split('.')[0]
    # 在数据库中存储路径
    cursor = connection.cursor()
    if saveState == "my_doc":
        cursor.execute('select file_name from file f where f.file_id in'
                       ' (select file_id from user_file where user_id = %s)', [userid])
        fileNamas = cursor.fetchall()
        for fileName in fileNamas:
            if str(fileName[0]) == filename:
                status = 200
                message = "文件名存在，请重新命名"
                break
            else:
                status = 2001
                message = "文件不存在，可以导入该文件"
    else:
        # 团队文档的名称是否重复
        cursor.execute("select file_name from file f, member_file mf "
                       "where f.file_id = mf.file_id and mf.team_mem_id in "
                       "(select team_mem_id from team_member where team_id = %s)", [teamId])
        fileNamas = cursor.fetchall()
        for fileName in fileNamas:
            if str(fileName[0]) == filename:
                status = 200
                message = "文件名存在，请重新命名"
                break
            else:
                status = 2001
                message = "文件不存在，可以导入该文件"
    return JsonResponse({"status": status, "message": message})


# 协作编辑
def cooperation_edite(request):
    fileId = request.POST.get("fileId")
    cursor = connection.cursor()
    cursor.execute("select content from file where file_id = %s", [fileId])
    doc_content = cursor.fetchone()[0]
    print("doc_content:", doc_content)
    return JsonResponse({'doc_content': doc_content})


def showrxcel(request):
    return render(request, "excel.html")


# 还原版本
def getoldEdition(request):
    saveState = request.GET.get("saveState")
    content = request.GET.get("content")
    user_id = request.GET.get("user_id")
    fileId = request.GET.get("fileId")

    cursor = connection.cursor()
    cursor.execute('select file_name from file f '
                   'where f.file_id = %s',
                   [fileId])
    file_name = cursor.fetchone()[0]
    cursor.execute("update file set content = %s where file_id = %s", [content, fileId])

    request.session["file_name"] = file_name
    request.session["doc_content"] = content
    request.session["file_id"] = fileId
    return render(request, "modify_RTFdocs.html", {"saveState": saveState})


# 删除版本
def delectEdition(request):
    saveState = request.GET.get("saveState")
    content = request.GET.get("content")
    user_id = request.GET.get("user_id")
    fileId = request.GET.get("fileId")
    editionid = request.GET.get("ediId")

    cursor = connection.cursor()
    cursor.execute('select file_name from file f '
                   'where f.file_id = %s',
                   [fileId])
    file_name = cursor.fetchone()[0]
    cursor.execute('delete from edition where edi_id=' + editionid)

    request.session["file_name"] = file_name
    request.session["doc_content"] = content
    request.session["file_id"] = fileId
    return render(request, "modify_RTFdocs.html", {"saveState": saveState})
