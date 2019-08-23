from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import connection, transaction
from document.models import  User
import time  # 引入time模块
import json  # 引入json模块


# 跳转到主页面
def index(request):
    # 模拟登录时把用户名和id存取在session里
    request.session['username'] = "吴炎"
    request.session['userId'] = 1
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
            cursor.execute('select team_id from Team where team_name=%s', [teamName])
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
            cursor.execute('insert into Team(team_name,user_id,date) value(%s,%s,%s)', [teamName, userId,formatTime])
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
            cursor.execute('select team_id from Team where team_name=%s', [teamName])
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
    cursor.execute('select DISTINCT role_name from role r,member_role mr,team_member tm,user u ' +
                   'where r.role_id=mr.role_id and mr.team_mem_id=tm.team_mem_id and tm.user_id=u.user_id and u.user_name="' + username + '"')
    result = cursor.fetchone()
    if result[0] == '管理员' or result[0] == '超级管理员':
        try:
            cursor = connection.cursor()
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
            cursor.close()
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
    doc_content = request.POST.get('doc_content', 0)  # 文档内容
    doc_title = request.POST.get('doc_title', 0)  # 文档标题
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

        cursor.execute("insert into user_file(user_id,file_id) values (%s,%s)", [1, file_id])
        return_param['saveStatus'] = "success"
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
        file_id = cursor.fetchone()
        # 获取团队成员id
        cursor.execute("select team_mem_id from team_member where user_id=%s and team_id = %s;", [1, teamId])
        team_mem_id = cursor.fetchone()
        # 保存团队文件
        cursor.execute("insert into member_file(team_mem_id, file_id) values (%s,%s)", [team_mem_id, file_id])
        return_param['saveStatus'] = "success"
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
    # userId = request.POST.get('userId')  # 获取用户Id
    userId=request.session.get('userId')
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
    cursor = connection.cursor()
    # 获取session里存放的username
    username = request.session.get('username')
    cursor.execute('select f.file_name,u.user_name,f.cre_date,u.user_id,f.file_id '
                   'from user u,file f,user_file uf '
                   'where u.user_id=uf.user_id and f.file_id=uf.file_id and u.user_name ="' + username + '" order by f.cre_date desc')
    row = cursor.fetchall()
    cursor.close()
    return JsonResponse({"list": row})


# 修改doc文档
def doc_modify(request):
    file_name = request.POST.get("file_name")  # 获取文件名称
    user_id = request.POST.get("user_id")  # 获取文件作者或团队的id
    saveState = request.POST.get("saveState")  # 获取文件状态
    fileId = request.POST.get("fileId")  # 获取文件状态

    cursor = connection.cursor()
    cursor.execute('select content from file f '
                   'where f.file_id = %s',
                   [fileId])
    doc_content = cursor.fetchone()[0]
    request.session["file_name"] = file_name
    request.session["doc_content"] = doc_content
    request.session["file_id"] = fileId
    return HttpResponse(json.dumps({'data': 'success'}))


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
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute('select DISTINCT role_name from role r,member_role mr,team_member tm,user u ' +
                   'where r.role_id=mr.role_id and mr.team_mem_id=tm.team_mem_id and tm.user_id=u.user_id and u.user_name="' + username + '"')
    result = cursor.fetchone()
    if result[0] == '管理员' or result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 修改角色
            cursor.execute('update member_role set role_id=(select role_id from role where role_name="'+roleName+'") where mem_role_id='+memRoleId)
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
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute('select DISTINCT role_name from role r,member_role mr,team_member tm,user u ' +
                   'where r.role_id=mr.role_id and mr.team_mem_id=tm.team_mem_id and tm.user_id=u.user_id and u.user_name="' + username + '"')
    result = cursor.fetchone()
    if result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 修改角色
            cursor.execute('update member_role set role_id=(select role_id from role where role_name="'+roleName+'") where mem_role_id='+memRoleId)
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
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute('select DISTINCT role_name from role r,member_role mr,team_member tm,user u ' +
                   'where r.role_id=mr.role_id and mr.team_mem_id=tm.team_mem_id and tm.user_id=u.user_id and u.user_name="' + username + '"')
    result = cursor.fetchone()
    if result[0] == '管理员' or result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 移除角色
            cursor.execute('delete tm,mr from team_member tm,member_role mr where tm.team_mem_id=mr.team_mem_id and mr.mem_role_id='+memRoleId)
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
    # 获取session里存放的username
    username = request.session.get('username')
    # 判断此登录的用户是否是管理员或者超级管理员，只有角色是管理员才有权限修改
    cursor = connection.cursor()
    cursor.execute('select DISTINCT role_name from role r,member_role mr,team_member tm,user u ' +
                   'where r.role_id=mr.role_id and mr.team_mem_id=tm.team_mem_id and tm.user_id=u.user_id and u.user_name="' + username + '"')
    result = cursor.fetchone()
    if result[0] == '超级管理员':
        # 创建保存点
        saveId = transaction.savepoint()
        try:
            # 角色修改为可编辑
            cursor.execute('update member_role set role_id=(select role_id from role where role_name="可编辑") where mem_role_id='+memRoleId)
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


# 分页
# def paginator_view(request):
#     cursor = connection.cursor()
#     cursor.execute('select * from Permission ')
#     list = cursor.fetchall()
#     # 将数据按照规定每页显示 10 条, 进行分割
#     paginator = Paginator(list, 3)
#     if request.method == "GET":
#         # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
#         page = request.GET.get('page')
#         try:
#             books = paginator.page(page)
#         except PageNotAnInteger:
#             # 如果请求的页数不是整数, 返回第一页。
#             books = paginator.page(1)
#         except InvalidPage:
#             # 如果请求的页数不存在, 重定向页面
#             return HttpResponse('找不到页面的内容')
#         except EmptyPage:
#             # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
#             books = paginator.page(paginator.num_pages)
#     return render(request, "fenye.html", {'books': list})
# 查询团队文档
# 团队文件
# 团队文件
def teamfile(request):
    teamname = request.POST.get("teamName")
    cursor = connection.cursor()
    cursor.execute('select t.team_id,t.team_name,u.user_id,u.user_name,mf.file_id,f.file_name,f.cre_date,f.file_id '
                   'from team t,team_member tm,member_file mf,file f ,user u where t.team_id=tm.team_id'
                   ' and tm.user_id=u.user_id and tm.team_mem_id=mf.team_mem_id and mf.file_id=f.file_id '
                   'and  t.team_name ="' + teamname + '"order by f.cre_date desc')
    list = cursor.fetchall()
    cursor.close()
    return JsonResponse({"list": list})

# 保存个人文件版本
@transaction.atomic
def saveEdition(request):
    # 获取用户名,版本内容,获取文件名称
    username = request.session.get('username')
    content = request.POST.get('content')
    filename = request.POST.get('filename')
    # 获取当前时间
    localTime = time.localtime(time.time())
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
    sid = transaction.savepoint()
    try:
        cursor = connection.cursor()
        # 获取用户名、id
        userid = int(cursor.execute('select user_id from user where user_name="' + username + '"'))
        cursor.execute("select file_id from file where file_name = %s", [filename])
        fileId = cursor.fetchone()
        # 保存版本
        cursor.execute('insert into edition (save_date,content) values(% s, % s)', [formatTime, content])
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
    except Exception as e:
        transaction.savepoint_rollback(sid)
    return JsonResponse({'status': 200})

# 查看个人版本
def getuseredition(request):
    cursor = connection.cursor()
    # 获取用户名
    username = request.session.get('username')
    # 获取文件名称、id、内容
    filename = request.POST.get('filename')
    fileid = int(cursor.execute('select file_id from file where file_name="' + filename + '"'))
    cursor.execute('select  u.user_name,f.file_name,e.save_date, e.content '
                   'from user u,file f,user_edition ue,user_file uf,edition e '
                   'where u.user_id=uf.user_id and uf.file_id=f.file_id and ue.edi_id=e.edi_id '
                   'and u.user_name = %s and f.file_id = %s', [username, fileid])
    list = cursor.fetchall()
    cursor.close()
    for l in list:
        print(l)
    return JsonResponse({"list": list})


# 登录页面
def login(requset):
    return render(requset, "login.html")


# 保存团队文件版本
@transaction.atomic
def saveTeamEdition(request):
    # 获取团队名、成员名、版本内容、文件名
    teamname = request.POST.get('teamName')
    member = request.session.get('username')
    content = request.POST.get('content')
    filename = request.POST.get('filename')
    # 获取当前时间
    localTime = time.localtime(time.time())
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
    sid = transaction.savepoint()
    try:
        cursor = connection.cursor()
        # 获取userid和fileid
        userid = int(cursor.execute('select user_id from user where user_name="' + member + '"'))
        cursor.execute("select file_id from file where file_name = %s", [filename])
        fileId = cursor.fetchone()
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
        transaction.savepoint_commit(sid)
    except Exception as e:
        transaction.savepoint_rollback(sid)
    return JsonResponse({'status': 200})

# 查看团队版本
def getTeamEdition(request):
    cursor = connection.cursor()
    # 获取空间名、文件名、id、内容
    teamname = request.session.get('teamName')
    filename = request.POST.get('filename')
    fileid = int(cursor.execute('select file_id from file where file_name="' + filename + '"'))
    cursor.execute(
        'select t.team_name,u.user_name,f.file_id,e.save_date,e.content from team t,team_member tm,member_file mf,member_edition me,user u ,file f,edition e '
        'where t.team_id=tm.team_id and tm.user_id=u.user_id and tm.team_mem_id=mf.team_mem_id and  mf.file_id=f.file_id and mf.mem_file_id=me.mem_file_id and me.edi_id=e.edi_id '
        'and t.team_name = %s and f.file_id = %s', [teamname, fileid])
    list = cursor.fetchall()
    cursor.close()
    return JsonResponse({"list": list})

# 我的回收站
def myBin(request):
    # 获取session的用户
    username = request.session['username']
    # 获取状态为1的属于此用户的文件和团队
    cursor=connection.cursor()
    cursor.execute('select * from( '
                   '(select distinct t.team_name, t.date time,t.team_id,t.what from user u, team t, team_member tm'
                   ' where u.user_id=tm.user_id and t.team_id=tm.team_id and t.team_state=1 and u.user_name="'+username+'")'
                   ' UNION'
                   ' (select f.file_name, f.cre_date time,f.file_id,f.type from file f, user u, user_file uf'
                   ' where f.file_id=uf.file_id and u.user_id=uf.user_id'
                   ' and f.file_state=1 and u.user_name="'+username+'")'
                   ' )t ORDER BY time DESC')
    result=cursor.fetchall()
    return JsonResponse({'status': 200, 'message':result})

# 回收站恢复文件
def restore(request):
    id=request.POST['id']
    what=request.POST['what']
    cursor = connection.cursor()
    # 判断该文件是文档还是协作空间
    if what == '协作空间':
        row=cursor.execute('update team set team_state=0 where team_id=' + id)
    else:
        row=cursor.execute('update file set file_state=0 where file_id=' + id)
    cursor.close()
    if row==1:
        return JsonResponse({'status': 200, 'message':'已成功恢复文件至协作空间'})
    else:
        return JsonResponse({'status': 4001, 'message': '出现错误'})

# 回收站彻底删除文件
def deleteAll(request):
    id=request.POST['id']
    what=request.POST['what']
    cursor = connection.cursor()
    try:
        # 判断该文件是文档还是协作空间
        if what == '协作空间':
            cursor.execute('delete f,mf,mr,tm,t from file f,member_file mf,member_role mr,team_member tm,team t where f.file_id=mf.file_id and mf.team_mem_id=tm.team_mem_id and mr.team_mem_id=tm.team_mem_id and tm.team_id=t.team_id and t.team_id='+id)
        else:
            cursor.execute('delete uf,f from user_file uf,file f where uf.file_id=f.file_id and f.file_id='+id)
            cursor.execute('delete mf,f from member_file mf,file f where mf.file_id=f.file_id and f.file_id=' + id)
        cursor.close()
        return JsonResponse({'status': 200, 'message': '删除成功'})
    except:
        cursor.close()
        return JsonResponse({'status': 4004, 'message': '删除失败'})
# 搜索文件
def searchFile(request):
    cursor = connection.cursor()
    searchCondition = request.POST.get("searchCondition")  # 获取查询条件
    searchedFiles = []
    files = {}

    # 查文件名
    cursor.execute("select file_id from file where file_name like '%" + searchCondition + "%'")
    fileIds = cursor.fetchall()
    for fileId in fileIds:
        # 根据查询到的fileID来获取file的详细数据
        cursor.execute(
            "select file_name,content,type,cre_date,file_id from file where file_id = %s and file_state = %s",
            [fileId[0], 0])
        searchList = cursor.fetchone()
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
    return_param = {}
    cursor = connection.cursor()
    cursor.execute("select file_id, file_name, content from file where file_id = %s", [file_id])
    fileCodition = cursor.fetchone()
    request.session["file_id"] = fileCodition[0]
    request.session["file_name"] = fileCodition[1]
    request.session["doc_content"] = fileCodition[2]
    return render(request, "modify_RTFdocs.html", return_param)
    return render(request, "modify_RTFdocs.html", return_param)