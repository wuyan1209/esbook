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
    return render(request, 'RTFdocs.html')


# 测试
def mysql_text(request):
    # 查新语句
    list = Permission.objects.raw('select * from Permission')
    content = {'list': list}
    return render(request, 'demo.html', content)
def select(request):
    cursor = connection.cursor()
    '''
    cursor.execute('select user_name,team_name from User,Team where User.user_id=Team.user_id')
    row = cursor.fetchall()
    for i in row:
        print(i[0]+"  "+i[1])
    '''
    cursor.execute('select team_name from team, team_member, user '
                   'where team.team_id = team_member.team_id and team_member.user_id = user.user_id '
                   'and user.user_name = "吴炎"' )
    result = cursor.fetchall()
    print(result)
    cursor.close()
    return HttpResponse(result)


# 添加协作空间
@csrf_exempt
def addTeam(request):
    if request.is_ajax():
        cursor = connection.cursor()
        # 获取空间名
        teamName = request.POST['teamName']
        # 空间名是唯一的，查询是否在数据库里存在
        cursor.execute('select team_id from Team where team_name=%s', [teamName])
        tid = cursor.fetchone()
        if tid:
            return JsonResponse({'status': 10023, 'message': '协作空间名字已存在，请换个名字'})
        # 从session里获取当前登录用户
        username = request.session.get('username')
        # 通过用户名获取该用户的id
        userId = User.objects.get(user_name=username).user_id
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
        return JsonResponse({'status': 200, 'message': '添加成功'})


# 主页面查询该成员加入的协作空间
@csrf_exempt
def getAllTeam(request):
    if request.is_ajax():
        cursor = connection.cursor()
        #获取session里存放的username
        username = request.session.get('username')
        cursor.execute('select team_name from team, team_member, user '
                       'where team.team_id = team_member.team_id and team_member.user_id = user.user_id '
                       'and user.user_name ="'+username+'" ')
        result = cursor.fetchall()
        cursor.close()
        return JsonResponse({'status': 200, 'message': result})


# Ajax异步保存富文本文档内容
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
        print("hai dui de ")
        cursor.execute("select file_id from file where file_name = %s", [doc_title])
        file_id = cursor.fetchone()
        print(file_id)
        cursor.execute("insert into user_file(user_id,file_id) values (%s,%s)", [2, file_id])
        return_param['saveStatus'] = "success"
        transaction.savepoint_commit(sid)
    except Exception as e:
        # 数据库更新失败
        return_param['saveStatus'] = "fail"
        transaction.savepoint_rollback(sid)
    return HttpResponse(json.dumps(return_param))
