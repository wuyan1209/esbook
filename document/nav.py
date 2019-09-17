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


# 我的收藏
def openMyCollection(request):
    page = request.POST['page']
    # 获取session里存放的userId
    userId = int(request.session.get('userId'))
    # 每页显示条数
    pageSize = 10
    cursor = connection.cursor()
    # 从collection表中获取用户收藏的文件总数
    cursor.execute('select count(1) from collection where user_id = %s', [userId])
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
                       'from user u,file f,collection c '
                       'where u.user_id = %s and f.file_id = c.file_id and f.file_id in (select file_id from collection where user_id = %s)'
                       'order by f.cre_date desc limit %s,%s',
                       [userId, userId, offset, pageSize])
        list = cursor.fetchall()
        cursor.close()
        return JsonResponse(
            {'status': 200, "page": int(page), "pageSize": pageSize, "totalPage": totalPage, "list": list})
    return JsonResponse({'status': 2001, 'message': '暂无数据'})
