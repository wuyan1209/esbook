import os, docx
from esbook.settings import BASE_DIR
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import connection, transaction


def createDocs(request):
    path = os.path.join(BASE_DIR, "static/docs")
    if not os.path.exists(path):
        os.makedirs(path)

    fileId = request.POST.get("file_id")
    cursor = connection.cursor()
    cursor.execute("select file_name, type, content from file where file_id = %s", [fileId])
    fileList = cursor.fetchone()
    fileName = fileList[0]
    fileType = fileList[1]
    content = fileList[2]
    switch = {0: ".docx", 1: ".xls", 2: ".ppt"}
    filePath = path + os.path.sep + fileName + switch[fileType]
    with open(filePath, 'w') as f:
        f.write(content)
    start = filePath.index("static")
    filePath = filePath[start:]
    return JsonResponse({"flag": "success", "DocURL": filePath})
