from django.urls import path
from document import views

urlpatterns = [
    # 主页面
    path('index/', views.index),
    # 新增docs
    path('RTFdocs/', views.RTFdocs),
    # 添加协作空间
    path('addTeam/', views.addTeam),
    # 修改协作空间
    path('editTeam/', views.editTeam),
    # 主页面查询该成员加入的协作空间
    path('getAllTeam/', views.getAllTeam),
    # 保存个人空间的docs
    path('saveDocTest/', views.RTFdocs_save),
    # 保存协作空间的docs
    path('saveTeamDoc/', views.saveTeamDoc),
    # 查找用户
    path('serachUser/', views.serachUser),
    # 添加协作成员
    path('addMember/', views.addMember),
    # 文档名称是否重复
    path('docNameExist/', views.docNameExist),
    # 修改doc文档
    path('docsModify/', views.docsModify),
    # 私人文件列表
    path('filelist/', views.fileList),
    # 打开修改文档
    path('modifyRTFdocs/', views.modifyRTFdocs),
    # 保存修改文档
    path('ajax_modify_RTFdoc/', views.ajax_modify_RTFdoc),
    # 查找协作空间的普通协作者
    path('serachTeamUser/', views.serachTeamUser),
    # 查找协作空间的管理者
    path('serachTeamAdmin/', views.serachTeamAdmin),
    # 修改协作者的角色
    path('editMemberRole/', views.editMemberRole),
    # 修改协作者为超管
    path('editAdminRole/', views.editAdminRole),
    # 协作者角色移除
    path('delMemberRole/', views.delMemberRole),
    # 协作者管理员角色移除，改为可编辑
    path('delAdminRole/', views.delAdminRole),
    # 删除协作空间，放到回收站
    path('delTeam/', views.delTeam),
    # 团队文件
    path('teamfile/', views.teamfile),
    # 查看版本
    path('getuseredition/', views.getuseredition),
    # 保存版本
    path('saveEdition/', views.saveEdition),
    # 登录页面
    path('login/', views.login),
    # 查看团队版本
    path('getTeamEdition/', views.getTeamEdition),
    # 保存团队版本
    path('saveTeamEdition/', views.saveTeamEdition),
    # 删除保本
    path('delectEdition/', views.delectEdition),
    # 判断版本内容是否重复
    path('editionExits/', views.editionExits),
    # 我的回收站
    path('myBin/', views.myBin),
    # 回收站恢复文件
    path('restore/', views.restore),
    # 回收站彻底删除文件
    path('deleteAll/', views.deleteAll),
    # 按文件名和文件内容搜索
    path('searchFile/', views.searchFile),
    # 打开搜索到的文件
    path('serachRTFdoc/', views.serachRTFdoc),
    # 跳转注册页面
    path('register/', views.register),
    # 删除文件
    path('delFiles/', views.delFiles),
    # 校验用户名
    path('valiName/', views.valiName),
    # 校验手机号
    path('valiPhone/', views.valiPhone),
    # 校验邮箱号
    path('valiEmail/', views.valiEmail),
    # 注册
    path('Register/', views.Register),
    # 登录
    path('userLogin/', views.userLogin),
    # 退出登录
    path('logout/', views.logout),
    # 个人中心
    path('personal/', views.personal),

    # 个人文件上传
    path("user_upload_file/", views.user_upload_file),
    # 团队文件上传
    path("team_upload_file/", views.team_upload_file),
    # 判断导入文件名是否重复
    path('uploadexist/', views.uploadexist),
    # 协作编辑
    path('cooperation_edite/', views.cooperation_edite),
    #Excel
    path('excel/',views.showrxcel),
    # 还原
    path('getoldEdition/', views.getoldEdition),
    # 重命名文件
    path('renameFiles/', views.renameFiles),
    #判断表格名称是否重复
    path('excelNameExist/',views.excelNameExist),
    #保存个人excel
    path('saveuserExcel/',views.saveuserExcel)

]
