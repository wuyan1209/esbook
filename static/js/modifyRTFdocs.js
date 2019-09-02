// 导入CKEditor
DecoupledEditor
    .create(document.querySelector('#editor'), {
            heading: {
                options: [
                    {model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph'},
                    {model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1'},
                    {model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2'},
                    {model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3'},
                    {model: 'heading4', view: 'h4', title: 'Heading 4', class: 'ck-heading_heading4'},
                    {model: 'heading5', view: 'h5', title: 'Heading 5', class: 'ck-heading_heading5'},
                    {model: 'heading6', view: 'h6', title: 'Heading 6', class: 'ck-heading_heading6'}
                ]
            },
            language: 'zh-cn',
            ckfinder: {
                options: {
                    resourceType: 'Images'
                },
                uploadUrl: '/static/upload'

            }
        }
    )
    .then(editor => {
        const toolbarContainer = document.querySelector('#toolbar-container');

        toolbarContainer.appendChild(editor.ui.view.toolbar.element);
    })
    .catch(error => {
        console.error(error);
    })


$(function () {

    // 加载时获取文档标题
    var old_doc_title = $("#docs_title").val();     // 页面加载时获取文档名称
    var doc_save_state = $("#doc_save_state").val();    // 文件状态 “my_doc”：个人  else：团队
    var userId = $("#userId").val();    // 用户的id
    var teamId = $("#teamId").val();    // 团队的id

    // 点击保存按钮保存
    $("#CKEditor_data_modify").on("click", function () {
        modifyDocs(old_doc_title, doc_save_state, userId, teamId);
    });

    //点击保存版本
    $("#saveedi").on("click", function () {
        if (doc_save_state == "my_doc") {
            // 保存个人版本
            // modifyDocs(old_doc_title, doc_save_state, userId, teamId)
            saveEdition();
        } else {
            // 保存团队的版本
            // modifyDocs(old_doc_title, doc_save_state, userId, teamId)
            saveTeamEditor(teamId);
        }
    });

    // ctrl+s 保存
    $("#editor").keydown(function (e) {
        if (e.keyCode == 83 && e.ctrlKey) {
            e.preventDefault();
            modifyDocs(old_doc_title, doc_save_state, userId, teamId);
        }
    });

    // 修改文档名称不能重复
    $("#docs_title").change(function () {
        var docsName = $(this).val();
        $.ajax({
            url: '/docNameExist/',
            type: 'post',
            data: {
                docsName: docsName,
                saveState: doc_save_state,
                userId: userId,
                teamId: teamId
            },
            dataType: 'json',
            success: function (data) {
                if (data.Exist == "YES") {
                    $("#docs_title").val(old_doc_title);
                    alert("文档名字不能重复，请重新填写")
                }
            }
        });
    });

    $(".close").click(function () {
        $("#myEditor").alert();
    });

    // 点击查看版本
    $("#showEditor").on("click", function () {
        $("#myEditor").show()
        if (doc_save_state == "my_doc") {
            //查看个人版本
            getEdition();
        } else {
            // 查看团队的版本
            getTeamEditor(teamId);
        }
    });

    // 关闭版本框
    $("#closeEditor").click(function () {
        $("#myEditor").hide()
    })
    $("#myEditor").hide()



    $("#editor").bind("DOMSubtreeModified", function () {
        setTimeout(function () {
            modifyDocs();
        }, 0);
    });


});

// 回显文档数据
doc_content();

// 回显数据
function doc_content() {
    var doc_content = $("#get_doc_content").val()
    $("#editor").html("");
    $("#editor").html(doc_content);
}

// 打开已存在文档
function docs_modify(name, id, saveState, fileId) {
    $.ajax({
        url: '/docsModify/',
        type: 'post',
        data: {
            file_name: name,
            user_id: id,
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

// 保存文档
function modifyDocs() {
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //取得html格式的内容
    var fileId = $("#fileId").val()
    var now_doc_title = $("#docs_title").val();  //取得文档标题
    if (now_doc_title == null || now_doc_title == "") {
        alert("请输入文档名称");
        return;
    }

    $.ajax({
        type: 'POST',
        url: '/ajax_modify_RTFdoc/',
        dataType: "json",
        data: {
            doc_content: doc_content,
            now_doc_title: now_doc_title,
            fileId: fileId
        },
        success: function (data) {
            if (data.saveStatus == "success") {
                // 保存成功
                //alert("保存成功了");
            } else {
                // 保存失败
                alert("保存失败了");
            }
        }
    })
}


// 保存个人版本
function saveEdition() {
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //获取当前版本内容
    var now_doc_title = $("#docs_title").val();  //取得当前文档标题

    //判断版本是否存在
    $.ajax({
        type: 'POST',
        url: '/editionExits/',
        dataType: "json",
        data: {
            content: doc_content,
        },
        success: function (data) {
            if (data.Exist == "YES") {
                alert("已成功创建内容，不需重复创建")
            } else {
                $.ajax({
                    type: 'POST',
                    url: '/saveEdition/',
                    dataType: "json",
                    data: {
                        content: doc_content,
                        filename: now_doc_title
                    },
                    success: function (data) {
                        if (data.status == 200) {
                            // 保存成功
                            alert(data.message);
                        } else {
                            // 保存失败
                            alert(data.message);
                        }
                    }
                })
            }
        }
    })
}

//保存团队版本
function saveTeamEditor() {
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //取得html格式的内容
    var now_doc_title = $("#docs_title").val();  //取得文档标题

    //判断版本是否存在
    $.ajax({
        type: 'POST',
        url: '/editionExits/',
        dataType: "json",
        data: {
            content: doc_content,
        },
        success: function (data) {
            if (data.Exist == "YES") {
                alert("已成功创建版本，不需重复创建")
            } else {
                $.ajax({
                    type: 'POST',
                    url: '/saveTeamEdition/',
                    dataType: "json",
                    data: {
                        content: doc_content,
                        filename: now_doc_title,
                        // teanid:teamId,
                    },
                    success: function (data) {
                        if (data.status == 200) {
                            // 保存成功
                            alert(data.message);
                        } else {
                            // 保存失败
                            alert(data.message);
                        }
                    }
                })
            }
        }
    })

}

//查看个人版本
function getEdition() {
    var now_doc_title = $("#docs_title").val();  //取得文档标题
    $.ajax({
        type: 'POST',
        url: '/getuseredition/',
        dataType: "json",
        data: {
            filename: now_doc_title,
        },
        success: function (data) {
            if (data.status == 200) {
                $("#myEditor div").remove()
                //查看成功
                for (var i = 0; i < data.list.length; i++) {
                    time = data.list[i][2];
                    updatetime = time.substring(0, 10) + "  " + time.substring(11);
                    html = "<div  style=\"border: 1px gray solid;margin-top: 20px;height: 55px;\">\n" +
                        " <span style='display:block'>" + updatetime + "&nbsp;&nbsp;&nbsp;版本&nbsp;</span>\n" +
                        " <span style='display:block'>" + data.list[i][0] + "保存&nbsp;&nbsp;&nbsp;&nbsp;" +
                        "<a href= \'javascript:void (0)\' data-toggle=\'modal\' data-target=\'#selectModal\' onclick=\"passName('" + data.list[i][5] + "','" + updatetime + "','" + data.list[i][3] + "')\">预览</a>" +
                        "&nbsp;&nbsp;&nbsp;<a href= \"javascript:void (0)\" onclick=\"getoldEdition('" + data.list[i][3] + "')\">还原</a>&nbsp;&nbsp;&nbsp;<a href= \"javascript:void (0) \" onclick='delectEdition(" + data.list[i][4] + ")'>删除</a></span>\n" +
                        " </div>"
                    $("#myEditor").append(html);
                }
            } else {
                // 失败
                alert("查看失败了");
            }
        }
    })
}

//查看团队版本
function getTeamEditor(teamId,) {
    var now_doc_title = $("#docs_title").val();  //取得文档标题
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //取得html格式的内容

    $.ajax({
        type: 'POST',
        url: '/getTeamEdition/',
        dataType: "json",
        data: {
            filename: now_doc_title,
            teamid: teamId,
        },
        success: function (data) {
            if (data.status == 200) {
                $("#myEditor div").remove()
                //查看成功
                for (var i = 0; i < data.list.length; i++) {
                    time = data.list[i][3];
                    updatetime = time.substring(0, 10) + "  " + time.substring(11);
                    html = "<div  style=\"border: 1px gray solid;margin-top: 20px;height: 55px\">\n" +
                        "<span style='display:block'>" + updatetime + "&nbsp;&nbsp;&nbsp;版本&nbsp;</span>\n" +
                        "<span style='display:block'>" + data.list[i][1] + "保存&nbsp;&nbsp;&nbsp;&nbsp;" +
                        "<a href= \"javascript:void (0)\"data-toggle=\'modal\' data-target=\'#selectModal\' onclick=\"passName('" + data.list[i][2] + "','" + updatetime + "','" + data.list[i][4] + "')\">预览</a>" +
                        "&nbsp;&nbsp;&nbsp;<a href= \"javascript:void (0)\" onclick=\"getoldEdition('" + data.list[i][4] + "')\">还原</a>&nbsp;&nbsp;&nbsp;<a href= \"javascript:void (0)\" onclick='delectEdition(" + data.list[i][5] + ")'>删除</a></span>\n" +
                        "</div>"
                    $("#myEditor").append(html);
                }
            } else {
                // 失败
                alert("查看失败了");
            }
        }
    })
}

//删除版本
function delectEdition(ediId) {
    if (window.confirm("您确定要删除吗？")) {
        $.ajax({
            url: "/delectEdition/",
            type: "POST",
            dataType: "json",
            data: {
                "ediId": ediId,
            },
            success: function (data) {
                alert(data.message);
                window.location.href = '/index/';
            },
        });
    }
}

//版本预览 给模态框传值
function passName(filename, time, content) {
    $("#myModalLabel").html(filename + '&emsp;&emsp;&emsp;' + time)
    $(".modal-body").html(content)
}

//还原版本
function getoldEdition(content) {
    var doc_save_state = $("#doc_save_state").val();
    var doc_title = $("#docs_title").val();  //取得当前文档标题
    var teamId = $("#teamId").val();
    if (window.confirm("您确定要还原到该版本吗？")) {
        //获取文件名、版本内容
        $.ajax({
            type: 'POST',
            url: '/saveEditionRTFdoc/',
            dataType: "json",
            data: {
                content: content,
                fileName: doc_title,
            },
            success: function (data) {
                if (data.status == 200) {
                    // 成功
                    alert(data.message)
                    window.location.href = '/index/';
                } else {
                    // 失败
                    alert(data.message)
                }
            }
        })
    }
}