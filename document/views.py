from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection
# Create your views here.

#跳转到主页面
from document.models import Permission


def index(request):
    return render(request,'index.html')


def RTFdocs(request):
    return render(request, 'RTFdocs.html')

def mysql_text(request):
    # 查新语句
    list=Permission.objects.raw('select * from Permission')
    content={'list':list}
    return render(request,'demo.html',content)

def first(request):
    return render(request,'first.html')

