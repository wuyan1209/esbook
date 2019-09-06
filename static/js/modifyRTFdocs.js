var EDITOR = null;
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

            },
        }
    )
    .then(editor => {
        EDITOR = editor
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
    content = $("#editor").html();  // 页面加载时获取的文档内容
    content = $("#editor").html();  // 页面加载时获取的文档内容
    var fileId = $("#fileId").val()



    // 用户角色为只读时，不能对文件进行修改，不能保存、删除、还原版本
    var roleName=$("#roleName").val()
    if(roleName=='只读'){
        $("#docs_title").attr("readOnly", true); //文件名不能修改
        $("#editor").attr("contenteditable", false);     //编辑器内容不能修改
        $("#saveedi").attr("disabled", true);    // 版本保存按钮不可点击
    }



    // 点击保存按钮保存
    $("#CKEditor_data_modify").on("click", function () {
        modifyDocs(old_doc_title, doc_save_state, userId, teamId);
    });

    //点击保存版本
    $("#saveedi").on("click", function () {
        if (doc_save_state == "my_doc") {
            // 保存个人版本
            saveEdition();
        } else {
            // 保存团队的版本
            saveTeamEditor(teamId, fileId);
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
            getTeamEditor(teamId, fileId);
        }
    });

    // 关闭版本框
    $("#closeEditor").click(function () {
        $("#myEditor").hide()
    })

    // 页面加载时隐藏版本框
    $("#myEditor").hide()

    // 文档改变即保存文档
    $("#editor").bind("DOMSubtreeModified", function () {
        setTimeout(function () {
            var doc_content = $("#editor").html();
            if (doc_content == content) {
                return
            }
            modifyDocs();
            if (doc_save_state != "my_doc") {
                sendWebsocket(doc_content)
            }
        }, 0);
    });

});
// socket客户端
var ws;

// 连接sock
function init() {
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
        // data = data.replace(/\<br data-cke-filler=\"true\"\>/g, '\<br data-cke-filler=\\\"true\\\"\>');
        console.log(data)
        data = $.parseJSON(data);
        var cooperation_fileId = data.fileId;   //  被修改的文件的id
        var cooperation_userId = data.userId;   //  修改文件用户的id
        var cooperation_content = data.doc_content;     //  修改的内容
        // cooperation_content = cooperation_content.replace(/\<p\>\<\/p\>/g, '\<p data-cke-filler=\"true\"\>\<\/p\>');

        // 获取当前用户和文件的id
        var fileId = $("#fileId").val()
        var userId = $("#userId").val()

        if (cooperation_fileId == fileId && cooperation_userId != userId) {
            // 团队成员打开了同一个文件
            if (content != "" && content != cooperation_content) {
                content = cooperation_content;
                EDITOR.setData(cooperation_content);
            }
        }

        if (cooperation_fileId == fileId && cooperation_userId == userId) {
            // 修改文档本人
            content = $("#editor").html();
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
function sendWebsocket(doc_content) {

    // 1:文件已自动保存，团队成员更新页面
    var fileId = $("#fileId").val()
    var userId = $("#userId").val()

    doc_content = doc_content.replace(/\u200B/g, '');

    // doc_content = doc_content.replace(/\<br data-cke-filler=\"true\"\>/g, '');
    // doc_content = doc_content.replace(/\<br\>/g, '');
    // console.log(doc_content)
    var send_message = {'fileId': fileId, 'userId': userId, 'doc_content': encodeURIComponent(doc_content)}
    ws.send(JSON.stringify(send_message))
}

// 在界面上显示接收到的数据，将替换掉一些需要转义的字符
function output(str) {

    var log = document.getElementById("log");
    var escaped = str.replace(/&/, "&amp;").replace(/</, "&lt;").replace(/>/, "&gt;").replace(/"/, "&quot;"); // "
    log.innerHTML = escaped + "<br>" + log.innerHTML;
}

// 回显文档数据
doc_content();

// 回显数据
function doc_content() {
    var doc_content = $("#get_doc_content").val()
    $("#editor").html(doc_content)
}

// 打开已存在文档
function docs_modify(name, id, saveState, fileId,roleName) {
    window.location.href = "/docsModify/?saveState=" + saveState + "&file_name=" + name +
        "&user_id=" + id + "&fileId=" + fileId + "&roleName=" + roleName;
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
function saveTeamEditor(teamId, fileId) {
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
                        fileId: fileId,
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
                    //处理字符串中包含字符串
                    contents = data.list[i][3];
                    var str = " '" + data.list[i][3] + "'";
                    var reg = /\"/g;
                    str = str.replace(reg, '&quot;');//双引号 //&apos;单引号

                    time = data.list[i][2];
                    updatetime = time.substring(0, 10) + "  " + time.substring(11);
                    html = "<div  style=\"border: 1px gray solid;margin-top: 20px;height: 55px;\">\n" +
                        " <span style='display:block'>" + updatetime + "&nbsp;&nbsp;&nbsp;版本&nbsp;</span>\n" +
                        " <span style='display:block'>" + data.list[i][0] + "保存&nbsp;&nbsp;&nbsp;&nbsp;" +
                        "<a href= \'javascript:void (0)\' data-toggle=\'modal\' data-target=\'#selectModal\' onclick=\"passName('" + data.list[i][5] + "','" + updatetime + "'," + str + ")\">预览</a>" +
                        "&nbsp;&nbsp;&nbsp;<a href= \"javascript:void (0)\" onclick=\"getoldEdition(" + str + ")\">还原</a>&nbsp;&nbsp;&nbsp;<a href= \"javascript:void (0) \" onclick='delectEdition(" + data.list[i][4] + ")'>删除</a></span>\n" +
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
function getTeamEditor(teamId, fileId) {
    var now_doc_title = $("#docs_title").val();  //取得文档标题
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //取得html格式的内容
    $.ajax({
        type: 'POST',
        url: '/getTeamEdition/',
        dataType: "json",
        data: {
            fileId: fileId,
            teamid: teamId,
        },
        success: function (data) {
            if (data.status == 200) {
                $("#myEditor div").remove()
                //查看成功
                for (var i = 0; i < data.list.length; i++) {
                    //处理字符串中包含字符串
                    contents = data.list[i][4];
                    var str = " '" + data.list[i][4] + "'";
                    var reg = /\"/g;
                    str = str.replace(reg, '&quot;');//双引号 //&apos;单引号

                    time = data.list[i][3];
                    updatetime = time.substring(0, 10) + "  " + time.substring(11);
                    html = "<div  style=\"border: 1px gray solid;margin-top: 20px;height: 55px\">\n" +
                        "<span style='display:block'>" + updatetime + "&nbsp;&nbsp;&nbsp;版本&nbsp;</span>\n" +
                        "<span style='display:block'>" + data.list[i][1] + "保存&nbsp;&nbsp;&nbsp;&nbsp;" +
                        "<button class=\"btn0\" data-toggle=\'modal\' data-target=\'#selectModal\' onclick=\"passName('" + data.list[i][2] + "','" + updatetime + "'," + str + ")\">预览</button>" +
                        "&nbsp;&nbsp;&nbsp;<button class=\"btn0 reduction\"  onclick=\"getoldEdition(" + str + ")\">还原</button>&nbsp;&nbsp;&nbsp;<button class=\"btn0 del\" onclick='delectEdition(" + data.list[i][5] + ")'>删除</button></span>\n" +
                        "</div>"
                    $("#myEditor").append(html);
                }
                if($("#roleName").val()=='只读'){
                    $(".reduction").attr("disabled", true);
                    $(".del").attr("disabled", true);
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
    var saveState = $("#doc_save_state").val();
    var userId = $("#userId").val();
    var fileId = $("#fileId").val();

    if (window.confirm("您确定要删除该版本吗？删除之后将无法还原！")) {

        window.location.href = "/delectEdition/?saveState=" + saveState + "&content=" + content +
            "&user_id=" + userId + "&fileId=" + fileId + "&ediId=" + ediId;

    }
    // if (window.confirm("您确定要删除该版本吗？")) {
    //     $.ajax({
    //         url: "/delectEdition/",
    //         type: "POST",
    //         dataType: "json",
    //         data: {
    //             "ediId": ediId,
    //         },
    //         success: function (data) {
    //             alert(data.message);
    //
    //         },
    //     });
    // }
}

//版本预览 给模态框传值
function passName(filename, time, content) {
    $("#myModalLabel").html(filename + '&emsp;&emsp;&emsp;' + time)
    $(".modal-body").html(content)
}

//还原版本
function getoldEdition(content) {
    if (window.confirm("您确定要还原到该版本吗？")) {
        EDITOR.setData(content)
    }
}