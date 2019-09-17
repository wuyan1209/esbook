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


# 添加收藏和取消收藏
def collectionFiles(request):
    fileId = request.POST.get("file_id")
    text = request.POST.get("text")
    userId = request.session.get("userId")
    returnParam = {}
    cursor = connection.cursor()
    try:
        if text == "收藏":
            cursor.execute("insert into collection (user_id,file_id) values (%s,%s)", [userId, fileId])
            returnParam["flag"] = "success"
        else:
            cursor.execute("delete from collection where file_id = %s and user_id = %s", [fileId, userId])
            returnParam["flag"] = "success"
    except Exception as e:
        returnParam["flag"] = "fail"
        print(e)
    return JsonResponse(returnParam)

# 获取文件是不是收藏的文件
def selCollectionFiles(request):
    fileId = request.POST.get("file_id")
    userId = request.session.get("userId")
    return_param = {}
    cursor = connection.cursor()
    cursor.execute("select collection_id from collection where file_id = %s and user_id = %s", [fileId, userId])
    collectionId = cursor.fetchone()
    if collectionId:
        return_param["state"] = "exist"
    else:
        return_param["state"] = "notExist"
    return JsonResponse(return_param)

