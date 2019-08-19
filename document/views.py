from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt
from document.models import Permission, User
import time  # 引入time模块
import json  # 引入json模块


# 跳转到主页面
def index(request):
    # 模拟登录时把用户名存取在session里
    request.session['username'] = "吴炎"
    return render(request, 'index.html')


# 新建docs
def RTFdocs(request):
    saveState = request.GET.get("saveState")
    return render(request, 'RTFdocs.html', {'saveState': saveState})


# 测试
def demo(request):
    # 查新语句
    list = Permission.objects.raw('select * from Permission')
    content = {'list': list}
    return render(request, 'demo.html', content)


def select(request):
    cursor = connection.cursor()
    cursor.execute('select team_name from team, team_member, user '
                   'where team.team_id = team_member.team_id and team_member.user_id = user.user_id '
                   'and user.user_name = "吴炎"')
    result = cursor.fetchall()
    print(result)
    cursor.close()
    return HttpResponse(result)


# 添加协作空间
@transaction.atomic
def addTeam(request):
    if request.is_ajax():
        # 获取空间名
        teamName = request.POST['teamName']
        try:
            # 空间名是唯一的，查询是否在数据库里存在
            cursor = connection.cursor()
            cursor.execute('select team_id from Team where team_name=%s', [teamName])
            tid = cursor.fetchone()
            if tid:
                return JsonResponse({'status': 10023, 'message': '协作空间名字已存在，请换个名字'})
            # 从session里获取当前登录用户
            username = request.session.get('username')
            # 通过用户名获取该用户的id
            userId = User.objects.get(user_name=username).user_id
            # 创建保存点
            save_id = transaction.savepoint()
            # 添加协作空间
            cursor.execute('insert into Team(team_name,user_id) value(%s,%s)', [teamName, userId])
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


# 主页面查询该成员加入的协作空间
def getAllTeam(request):
    return_param = {}
    team_id = []
    team_name = []
    if request.is_ajax():
        cursor = connection.cursor()
        # 获取session里存放的username
        username = request.session.get('username')
        cursor.execute('select team.team_id, team_name from team, team_member, user '
                       'where team.team_id = team_member.team_id and team_member.user_id = user.user_id '
                       'and user.user_name ="' + username + '" ')
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
        cursor.execute("insert into file(file_name,content,cre_date) values(%s,%s,%s)",
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
    return_param = {}
    # 从数据库中查询文档标题
    cursor = connection.cursor()
    cursor.execute('select file_name from file f where f.file_id in'
                   ' (select file_id from user_file where user_id = 2)')
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
    cursor.execute('select f.file_name,u.user_name,f.cre_date,u.user_id '
                   'from user u,file f,user_file uf '
                   'where u.user_id=uf.user_id and f.file_id=uf.file_id and u.user_name ="' + username + '" order by f.cre_date desc')
    row = cursor.fetchall()
    cursor.close()
    return JsonResponse({"list": row})

# 修改doc文档
def doc_modify(request):
    file_name = request.POST.get("file_name")  # 获取文件名称
    user_id = request.POST.get("user_id")  # 获取文件作者

    cursor = connection.cursor()
    cursor.execute('select content from file f , user_file uf '
                   'where f.file_id = uf.file_id and f.file_name = %s and uf.user_id = %s',
                   [file_name, user_id])
    doc_content = cursor.fetchone()[0]
    request.session['doc_content'] = doc_content
    request.session['file_name'] = file_name
    return HttpResponse(json.dumps({'data': 'success'}))


# 修改页面
def modify_RTFdocs(request):
    return render(request, "modify_RTFdocs.html")


# 修改文档
@transaction.atomic
def ajax_modify_RTFdoc(request):
    doc_content = request.POST.get('doc_content')  # 文档内容
    now_doc_title = request.POST.get('now_doc_title')  # 当前文档标题
    old_doc_title = request.POST.get('old_doc_title')  # 原来文档标题
    localTime = time.localtime(time.time())  # 获取当前时间
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)  # 格式化当前日期 ‘年-月-日 时：分：秒’
    return_param = {}
    sid = transaction.savepoint()
    try:
        cursor = connection.cursor()
        # 数据库更新
        cursor.execute("update file set file_name = %s , content = %s, cre_date = %s where file_name = %s",
                       [now_doc_title, doc_content, formatTime, old_doc_title])
        return_param['saveStatus'] = "success"
        transaction.savepoint_commit(sid)
    except Exception as e:
        # 数据库更新失败
        return_param['saveStatus'] = "fail"
        transaction.savepoint_rollback(sid)
    return HttpResponse(json.dumps(return_param))
#分页
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
#查询团队文件
def teamfile(request):
    teamname=request.POST.get("teamName")
    cursor = connection.cursor()
    cursor.execute('select t.team_id,t.team_name,u.user_id,u.user_name,mf.file_id,f.file_name,f.cre_date '
                   'from team t,team_member tm,member_file mf,file f ,user u where t.team_id=tm.team_id'
                   ' and tm.user_id=u.user_id and tm.team_mem_id=mf.team_mem_id and mf.file_id=f.file_id '
                   'and  t.team_name ="' + teamname + '"order by f.cre_date desc')
    list = cursor.fetchall()
    cursor.close()
    return JsonResponse({"list": list})
