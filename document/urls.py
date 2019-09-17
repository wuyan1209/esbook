from django.urls import path
from document import views, mkdirDocs, clickMenu, nav,login


urlpatterns = [
    # 主页面
    path('index/', login.index),
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
    path('login/', login.login),
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
    path('register/', login.register),
    # 删除文件
    path('delFiles/', views.delFiles),
    # 校验用户名
    path('valiName/', login.valiName),
    # 校验手机号
    path('valiPhone/', login.valiPhone),
    # 校验邮箱号
    path('valiEmail/', login.valiEmail),
    # 邮箱验证码
    path('postEmail/',login.postEmail),
    # 注册
    path('Register/', login.Register),
    # 登录
    path('userLogin/', login.userLogin),
    # 退出登录
    path('logout/', login.logout),
    # 个人中心
    path('personal/', login.personal),
    # 查看密码是否正确
    path('conpwd/',login.conpwd),
    # 修改密码
    path('modifyPwd/',login.modifyPwd),
    # 重置密码页面
    path('resetPassword/',login.resetPassword),
    # 重置密码
    path('updatePwd/',login.updatePwd),

    # 个人文件上传
    path("user_upload_file/", views.user_upload_file),
    # 团队文件上传
    path("team_upload_file/", views.team_upload_file),
    # 判断导入文件名是否重复
    path('uploadexist/', views.uploadexist),
    # 协作编辑
    path('cooperation_edite/', views.cooperation_edite),
    # Excel
    path('excel/', views.showrxcel),
    # 还原
    path('getoldEdition/', views.getoldEdition),
    # 重命名文件
    path('renameFiles/', views.renameFiles),
    # 上传图片
    path('uploadImg/', login.uploadImg),
    # 获取个人信息
    path('getUser/',login.getUser),
    # 创建文件
    path('createDocs/', mkdirDocs.createDocs),
    # 判断表格名称是否重复
    path('excelNameExist/', views.excelNameExist),
    # 保存个人excel
    path('saveuserExcel/', views.saveuserExcel),
    # 收藏文件
    path('collectionFiles/', clickMenu.collectionFiles),
    # 查询文件是否已收藏
    path('selCollectionFiles/', clickMenu.selCollectionFiles),
    # 打开我的收藏
    path('openMyCollection/', nav.openMyCollection),
    # 跳转到excel页面
    path('excelModify/', views.excelModify),
    #保存excel内容
    path('saveExcel/',views.saveExcel),
    #保存团队的excel文件
    path('saveTeamExcel/', views.saveTeamExcel),
]
