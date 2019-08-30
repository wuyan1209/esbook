$(function () {
    // 创建文档
    $("#sure_doc").on("click", function () {
        var doc_name = $("#doc_name").val();
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

    $("#doc_name").on("input", function () {
        var doc_name = $("#doc_name").val();
        setTimeout(function () {
            if (flag) {
                if (doc_name == "" || doc_name == null) {
                    return
                }
                var teamId = 0
                if (saveState != "my_doc") {
                    teamId = saveState;
                }
                $.ajax({
                    url: "/docNameExist/",
                    type: "POST",
                    data: {docsName: doc_name, saveState: saveState, teamId: teamId},
                    dataType: "json",
                    success: function (data) {
                        if (data.Exist == "YES") {
                            $("#docNameExist").text("文件名已存在，请重新输入")
                            $("#doc_name").val("")
                        } else {
                            $("#docNameExist").text("")
                        }
                    }
                })

            }
        }, 0)
    })
});

function toModify(doc_name, userId, fileId) {
    $.ajax({
        url: '/docsModify/',
        type: 'post',
        data: {
            file_name: doc_name,
            user_id: userId,
            saveState: saveState,
            fileId: fileId
        },
        dataType: 'json',
        success: function (data) {
            if (data.data == "success") {
                window.location.href = "/modifyRTFdocs/?saveState=" + saveState;
            }
        }
    });
}