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

     // excel
    $("#sure_excel").on("click", function () {
        var excel_name = $("#excel_name").val();
        var excelflag = false
        // 判断文档名称是否为空
        if (excel_name == "" || excel_name == null) {
            alert("请输入文件名")
            return;
        }

        // 判断文档名称是否重复
        var teamId = 0
        if (saveState != "my_doc") {
            teamId = saveState;
        }
        $.ajax({
            url: "/excelNameExist/",
            type: "POST",
            async: false,
            data: {
                excelName: excel_name,
                saveState: saveState,
                teamId: teamId,
              },
            dataType: "json",
            success: function (data) {
                if (data.Exist == "YES") {
                    $("#excelNameExist").text("文件名已存在，请重新输入")
                    $("#excel_name").val("")
                }
                 if (data.Exist == "No"){
                    $("#excelNameExist").text("");
                    excelflag = true;
                }
            }
        });
        // 文件名不重复，可以创建文档
        if (excelflag) {
            $("#excel_name").val("");
            if (saveState == "my_doc") {
                $.ajax({
                    url: "/saveuserExcel/",
                    type: "POST",
                    data: {
                        excel_title: excel_name,
                        excel_content: "",
                    },
                    dataType: "json",
                    success: function (data) {
                        if (data.saveStatus == "success") {
                            toExcel(excel_name, data.userId, data.fileId)
                        }
                    }
                })
            } else {
                $.ajax({
                    url: "/saveTeamExcel/",
                    type: "POST",
                    data: {
                        doc_title: excel_name,
                        doc_content: "",
                        teamId: saveState
                    },
                    dataType: "json",
                    success: function (data) {
                        if (data.saveStatus == "success") {
                            sendWebsocket(saveState, data.fileId)
                            toExcel(excel_name, 0, data.fileId)
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

    // 输入框获得焦点清除提示内容
    $("#excel_name").focus(function () {
        $("#excelNameExist").text("")
    });

    // 关闭模态框清空文档名称
    $('#createDocs').on('hide.bs.modal', function () {
        $("#doc_name").val("")
    })

     // 关闭模态框清空文档名称
    $('#createExcel').on('hide.bs.modal', function () {
        $("#excel_name").val("")
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
});

function toModify(doc_name, userId, fileId) {
    window.location.href = "/docsModify/?saveState=" + saveState + "&file_name=" + doc_name +
        "&user_id=" + userId + "&fileId=" + fileId;
}

function toExcel(doc_name, userId, fileId) {
    window.location.href = "/excelModify/?saveState=" + saveState + "&file_name=" + doc_name +
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
