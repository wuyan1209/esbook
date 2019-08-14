from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db import connection
from django.views.decorators.csrf import  csrf_exempt
from document.models import Permission, User


#跳转到主页面
def index(request):
    #模拟登录时把用户名存取在session里
    request.session['username']="吴炎"
    return render(request,'index.html')


def RTFdocs(request):
    return render(request, 'RTFdocs.html')

def mysql_text(request):
    # 查新语句
    list=Permission.objects.raw('select * from Permission')
    content={'list':list}
    return render(request,'demo.html',content)

#添加写作空间（团队）
@csrf_exempt
def addTeam(request):
    if request.is_ajax():
        cursor = connection.cursor()
        # 获取空间名
        teamName = request.POST['teamName']
        # 空间名是唯一的，查询是否在数据库里存在
        cursor.execute('select team_id from Team where team_name=%s', [teamName])
        row = cursor.fetchone()
        if row:
            return JsonResponse({'status':10023,'message':'协作空间名字已存在，请换个名字'})
        # 从session里获取当前登录用户
        username = request.session.get('username')
        # 通过用户名获取该用户的id
        userId = User.objects.get(user_name=username).user_id
        # 添加协作空间
        cursor.execute('insert into Team(team_name,user_id) value(%s,%s)',[teamName,userId])
        cursor.close()
        return JsonResponse({'status':200,'message':'添加成功'})

def select(request):
    cursor=connection.cursor()
    cursor.execute('select user_name,team_name from User,Team where User.user_id=Team.user_id')
    row = cursor.fetchall()
    for i in row:
        print(i[0]+"  "+i[1])
    cursor.close()
    return HttpResponse(row)


