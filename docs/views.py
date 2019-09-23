from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db import connection, transaction
import time  # 引入time模块
import json  # 引入json模块
import os
from itertools import chain
from esbook.settings import BASE_DIR


def getDocsSaveState(request):
    fileId = request.POST.get("fileId")     #获取文件的id
    cursor = connection.cursor()
    # 查看该文件是个人文件还是团队文件
    cursor.execute("select file_id from user_file where file_id = %s", [fileId])
    userFileId = cursor.fetchone()
    saveState = ""
    if userFileId:
        saveState = "my_doc"
    cursor.execute(
        "select team_id from team_member tm, member_file mf where tm.team_mem_id = mf.team_mem_id and mf.file_id = %s",
        [fileId])
    memberFileId = cursor.fetchone()
    if memberFileId:
        saveState = memberFileId[0]
    return JsonResponse({"saveState": saveState})
