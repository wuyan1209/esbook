from django.urls import path
from document import views

urlpatterns = [
    # 主页面
    path('index/', views.index),
    # 新增docs
    path('RTFdocs/', views.RTFdocs),
    # 添加协作空间
    path('addTeam/', views.addTeam),
    # 测试
    path('mysql/', views.mysql_text),
    path('select/', views.select),
    # 主页面查询该成员加入的协作空间
    path('getAllTeam/', views.getAllTeam),
    # 增加协作空间
    path('addTeam/', views.addTeam),
    # 保存docs
    path('saveDocTest/', views.RTFdocs_save),
    # 文档名称是否重复
    path('docNameExist/', views.docNameExist),
    #私人文件列表
    path('filelist/', views.fileList)
]
