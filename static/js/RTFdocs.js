$(function () {
    // 创建文档
    $("#sure_doc").on("click", function () {
        var doc_name = $("#doc_name").val();
        var modify_flag = false
        // 判断文档名称是否为空
        if (doc_name == "" || doc_name == null) {
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
});

function toModify(doc_name, userId, fileId) {
    window.location.href = "/docsModify/?saveState=" + saveState+"&file_name=" + doc_name +
        "&user_id="+userId+"&fileId="+fileId;
}
