from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db import connection, transaction
import time  # 引入time模块
import json  # 引入json模块
import os
from itertools import chain
from esbook.settings import BASE_DIR


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
        # 查询所有收藏的file_id
        cursor.execute("select file_id from collection where user_id = %s", [userId])
        collectionFileIds = cursor.fetchall()
        collectionFileIds = list(chain.from_iterable(collectionFileIds))
        cursor.execute("select f.file_name, u.user_name,f.cre_date,u.user_id,f.file_id,f.type "
                       " from user u, file f, user_file uf"
                       " where f.file_id = uf.file_id and uf.file_id in %s"
                       " and u.user_id = %s"
                       " and f.file_state = 0"
                       " UNION "
                       " select distinct f.file_name, u.user_name, f.cre_date, u.user_id, f.file_id, f.type"
                       " from user u,file f,member_file mf,team_member tm"
                       " where f.file_id = mf.file_id"
                       " and mf.team_mem_id=tm.team_mem_id"
                       " and mf.file_id in %s"
                       " and tm.team_mem_id in (select team_mem_id from member_file where file_id in %s)"
                       " and tm.user_id = u.user_id"
                       " and f.file_state = 0"
                       " order by cre_date desc limit %s,%s",
                       [collectionFileIds, userId, collectionFileIds, collectionFileIds, offset, pageSize]
                       )
        collectionlist = cursor.fetchall()
        cursor.close()
        return JsonResponse(
            {'status': 200, "page": int(page), "pageSize": pageSize, "totalPage": totalPage, "list": collectionlist})
    return JsonResponse({'status': 2001, 'message': '暂无数据'})
