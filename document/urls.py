from django.urls import path, re_path
from document import views

urlpatterns = [
    # 主页面
    path('index/', views.index),
    # 新增docs
    re_path('RTFdocs/', views.RTFdocs),
    # 添加协作空间
    path('addTeam/', views.addTeam),
    # 测试
    path('demo/', views.demo),
    path('select/', views.select),
    # 主页面查询该成员加入的协作空间
    path('getAllTeam/', views.getAllTeam),

    # 保存个人空间的docs
    path('saveDocTest/', views.RTFdocs_save),
    # 保存协作空间的docs
    path('saveTeamDoc/', views.saveTeamDoc),
    # 查找用户
    path('serachUser/', views.serachUser),
    # 添加协作成员
    path('addMember/',views.addMember),

    # 文档名称是否重复
    path('docNameExist/', views.docNameExist),
    # 修改doc文档
    path('docsModify/', views.doc_modify),
    # 私人文件列表
    path('filelist/', views.fileList),
    # 打开修改文档
    path('modify_RTFdocs/', views.modify_RTFdocs),
    # 保存修改文档
    path('ajax_modify_RTFdoc/', views.ajax_modify_RTFdoc)


]
