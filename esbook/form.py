# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response

# 主页面
def index_form(request):
    return render_to_response('index.html')

# 文档编辑页面
def docs_form(request):
    return render_to_response('RTFdocs.html')
