from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
import time  # 引入time模块
import json  # 引入json模块
# Create your views here.

# 跳转到主页面
from django.views.decorators.csrf import csrf_exempt

from document.models import Permission


def index(request):
    return render(request, 'index.html')


def RTFdocs(request):
    return render(request, 'RTFdocs.html')


def mysql_text(request):
    # 查新语句
    list = Permission.objects.raw('select * from Permission')
    content = {'list': list}
    return render(request, 'demo.html', content)


def first(request):
    return render(request, 'first.html')


# Ajax异步保存富文本文档内容
def RTFdocs_save(request):
    doc_content = request.POST.get('doc_content', 0)  # 文档内容
    doc_title = request.POST.get('doc_title', 0)  # 文档标题
    localTime = time.localtime(time.time())  # 获取当前时间
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)  # 格式化当前日期 ‘年-月-日 时：分：秒’
    return_param = {}
    try:
        # 数据库更新
        cursor = connection.cursor()
        cursor.execute("insert into file(file_name,content,cre_date) values(%s,%s,%s)",
                       [doc_title, doc_content, formatTime])
        return_param['saveStatus'] = "success"
    except Exception as e:
        # 数据库更新失败
        return_param['saveStatus'] = "fail"
    return HttpResponse(json.dumps(return_param))
