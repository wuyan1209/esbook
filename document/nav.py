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

# 通过文件id查找用户在团队的角色
def getRoleName(request):
    fileId=request.POST['fileId']
    userId=request.session['userId']
    # 判断是自己文件还是团队文件
    cursor=connection.cursor()
    cursor.execute('select f.file_id from file f,user u,user_file uf '
                   'where f.file_id=uf.file_id and u.user_id=uf.user_id and f.file_id= '+fileId)
    result=cursor.fetchone()
    # 个人文件
    if result:
        return JsonResponse({'roleName': '超级管理员'})
    # 团队文件
    else:
        # 查找用户在此文件存在的团队内的角色
        cursor.execute('select r.role_name from team_member tm,member_role mr,role r '
                       'where tm.team_mem_id=mr.team_mem_id and mr.role_id=r.role_id '
                       'and tm.user_id=%s and tm.team_id=(select tm.team_id  from team_member tm,member_file mf,file f '
                       'where tm.team_mem_id=mf.team_mem_id and mf.file_id=f.file_id and f.file_id=%s)',[userId,fileId])
        roleName=cursor.fetchone()[0]
        return JsonResponse({'roleName':roleName})
