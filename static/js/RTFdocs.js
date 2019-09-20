$(function () {
    // 创建文档
    $("#sure_doc").on("click", function () {

        var doc_name = $("#doc_name").val();
        var modify_flag = false
        // 判断文档名称是否为空
        if (doc_name == "" || doc_name == null) {
            alert("请输入文件名")
            return;
        }

        // 判断文档名称是否重复
        var teamId = 0
        if (saveState != "my_doc") {
            teamId = saveState;
        }
        $.ajax({
            url: "/docNameExist/",
            type: "POST",
            async: false,
            data: {docsName: doc_name, saveState: saveState, teamId: teamId},
            dataType: "json",
            success: function (data) {
                if (data.Exist == "YES") {
                    $("#docNameExist").text("文件名已存在，请重新输入")
                    $("#doc_name").val("")

                } else {
                    $("#docNameExist").text("")
                    modify_flag = true
                }
            }
        });

        // 文件名不重复，可以创建文档
        if (modify_flag) {
            $("#doc_name").val("");
            if (saveState == "my_doc") {
                // 个人文档
                $.ajax({
                    url: "/saveDocTest/",
                    type: "POST",
                    data: {
                        doc_title: doc_name,
                        doc_content: "",
                    },
                    dataType: "json",
                    success: function (data) {
                        if (data.saveStatus == "success") {
                            toModify(doc_name, data.userId, data.fileId)
                        }
                    }
                })
            } else {
                // 团队文档
                $.ajax({
                    url: "/saveTeamDoc/",
                    type: "POST",
                    data: {
                        doc_title: doc_name,
                        doc_content: "",
                        teamId: saveState
                    },
                    dataType: "json",
                    success: function (data) {
                        if (data.saveStatus == "success") {
                            sendWebsocket(saveState, data.fileId)
                            toModify(doc_name, 0, data.fileId)
                        }
                    }
                })
            }
        }
    });


    // 输入框获得焦点清除提示内容
    $("#doc_name").focus(function () {
        $("#docNameExist").text("")
    });


    // 关闭模态框清空文档名称
    $('#createDocs').on('hide.bs.modal', function () {
        $("#doc_name").val("")
    })

    // 判断用户名是否重复
    var flag = true;
    $('#search-bar').on('compositionstart', function () {
        flag = false;
    });
    $('#search-bar').on('compositionend', function () {
        flag = true;
    });

    socketInit()

    // 删除文件
    $("#btnDel").on("click", function () {
        var file_id = $("#clickMenu").attr("file_id");
        var team_name = $("#clickMenu").attr("team_name");
        $.ajax({
            url: "/delFiles/",
            type: "post",
            data: {file_id: file_id},
            dataType: "json",
            success: function (data) {
                if (data.flag == "success") {
                    // 个人文档刷新
                    if (saveState == "my_doc") {
                        my_doc_file()
                    } else {
                        // 团队文档刷新
                        team_file(team_name)
                    }
                }
            }
        })
    });

    //重命名文件
    $("#confirmRename").on("click", function () {
        var file_id = $("#clickMenu").attr("file_id");
        var fileName = $("#renameFile").val();
        var team_name = $("#clickMenu").attr("team_name")
        var modify_flag = false
        // 判断文档名称是否为空
        if (fileName == "" || fileName == null) {
            alert("请输入文件名")
            return
        }

        // 判断文档名称是否重复
        var teamId = 0
        if (saveState != "my_doc") {
            teamId = saveState;
        }
        $.ajax({
            url: "/docNameExist/",
            type: "POST",
            async: false,
            data: {docsName: fileName, saveState: saveState, teamId: teamId},
            dataType: "json",
            success: function (data) {
                if (data.Exist == "YES") {
                    $("#renameExist").text("文件名已存在，请重新输入")
                    $("#doc_name").val("")

                } else {
                    $("#renameExist").text("")
                    modify_flag = true
                }
            }
        });
        // 文件名不重复，可以创建文档
        if (modify_flag) {
            $.ajax({
                url: "/renameFiles/",
                type: "post",
                data: {file_id: file_id, fileName: fileName},
                dataType: "json",
                success: function (data) {
                    if (data.flag == "success") {
                        $('#renameModel').modal('hide')
                        if (saveState == "my_doc") {
                            // 个人文档刷新
                            my_doc_file()
                        } else {
                            // 团队文档刷新
                            team_file(team_name)
                        }
                    }
                }
            })
        }
        // 关闭模态框清空文档名称
        $('#renameModel').on('hide.bs.modal', function () {
            $("#renameFile").val("")
        })

        // 输入框获得焦点清除提示内容
        $("#renameFile").focus(function () {
            $("#renameExist").text("")
        });
    })

    // 导出文件
    $("#btnExport").on("click", function () {
        var file_id = $("#clickMenu").attr("file_id");  // 文件的id
        $.ajax({
            url: "/createDocs/",
            type: "POST",
            data: {file_id: file_id},
            dataType: "json",
            success: function (data) {
                if (data.flag == "success") {
                    var filePath = data.DocURL;
                    window.location.href = "/" + filePath
                } else {
                    alert("导出失败")
                }
            }
        })
    });

    //阻止浏览器默认右击点击事件
    $("#tab").on("contextmenu", "tr", function () {
        return false;
    });

    // 绑定右击事件
    $("#tab").on("mousedown", "tbody tr", function (e) {
        //右键为3
        if (3 == e.which) {
            var file_id = $(this).attr("file_id");
            var team_name = $(this).attr("teamname");
            var fileState = $(this).attr("fileState");
            $.ajax({
                url: "/selCollectionFiles/",
                type: "POST",
                data: {file_id: file_id},
                dataType: "json",
                success: function (data) {
                    if (data.state == "exist") {
                        $("#flag").text("取消收藏");
                        $("#btnColImg").attr("src", "../static/assets/images/已收藏.png")
                    } else {
                        $("#flag").text("收藏");
                        $("#btnColImg").attr("src", "../static/assets/images/未收藏.png")
                    }
                }
            });

            $("#clickMenu").attr("file_id", file_id);
            $("#clickMenu").attr("team_name", team_name);
            $("#clickMenu").attr("fileState", fileState);

            $("#clickMenu").css("display", "block");
            //var divchild = $(this).children("div");
            $("#clickMenu").css("left", e.clientX - 250);
            $("#clickMenu").css("top", e.clientY - 50);
        }

        if ($("#roleName").val() == '只读') {
            // 只读用户限制不能导出，删除，重命名
            $("#btnDel").attr("disabled", "disabled");
            $("#btnRename").attr("disabled", "disabled");
            $("#btnExport").attr("disabled", "disabled");
        } else if (saveState == "my_collection") {
            // 非只读用户但是在我的收藏页面，不能删除和重命名，但是可以导出
            $("#btnDel").attr("disabled", "disabled");
            $("#btnRename").attr("disabled", "disabled");
            $("#btnExport").removeAttr("disabled");
        } else {
            //非只读用户不在我的收藏页面，没有限制
            $("#btnDel").removeAttr("disabled");
            $("#btnRename").removeAttr("disabled");
            $("#btnExport").removeAttr("disabled");
        }
    });

    // 点击空白区域隐藏菜单
    $("body").on("click", function () {
        $("#clickMenu").css("display", "none");
    });

    // 右键菜单鼠标悬浮阴影
    $("#clickMenu li").hover(function () {
        $(this).addClass("liHover");
    }, function () {
        $(this).removeClass("liHover");
    });

    // 收藏文档
    $("#btnCollection").parent().on("click", function () {
        var text = $("#flag").text();
        var file_id = $("#clickMenu").attr("file_id");
        $.ajax({
            url: "/collectionFiles/",
            data: {text: text, file_id: file_id},
            type: "POST",
            dataType: "",
            success: function (data) {
                if (data.flag == "success") {
                    if (text != "收藏") {
                        if (saveState == "my_collection") {
                            myCollectionFiles()
                        }
                    }
                }
            }
        })

    })
});

// 打开已存在文档
function toModify(doc_name, userId, fileId) {
    window.location.href = "/docsModify/?saveState=" + saveState + "&file_name=" + doc_name +
        "&user_id=" + userId + "&fileId=" + fileId;
}


function socketInit() {
    ws = new WebSocket("ws://47.105.172.29:9001/");

    // 连接WebSocket服务器成功，打开成功
    ws.onopen = function () {
        console.log("onopen");
    };

    // 收到WebSocket服务器数据
    ws.onmessage = function (e) {
        // e.data contains received string.

        // 团队中修改的文件的id
        var data = e.data;
        data = data.replace(/'/g, '"');

        data = $.parseJSON(data);
        var cooperation_team_name = data.team_name;   //  团队名称
        var cooperation_teamId = data.teamId;   //  团队id
        var cooperation_userId = data.userId;     //  修改的内容

        // 获取当前用户和文件的id
        var userId = $("#user").attr("userId")

        if (cooperation_teamId == saveState && cooperation_userId != userId) {
            // 同一个团队的不同用户
            // 更新文档页面
            team_file(cooperation_team_name)
        }
    };

    // 关闭WebSocket连接
    ws.onclose = function () {
        console.log("onclose");
    };

    // WebSocket连接出现错误
    ws.onerror = function (e) {
        console.log("onerror");
        console.log(e)
    };


}

// 发送内容到websocket
function sendWebsocket(teamId, fileId) {

    // 1:文件已自动保存，团队成员更新页面
    var userId = $("#user").attr("userId");
    var team_name = $("#h2").text();

    var send_message = {
        'team_name': encodeURIComponent(team_name),
        'userId': userId,
        'teamId': teamId,
        'doc_content': ""
    };
    ws.send(JSON.stringify(send_message))
}
