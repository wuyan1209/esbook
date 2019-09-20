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
            if (data.Exist == "No") {
                $("#excelNameExist").text("");
                excelflag = true;
            }
        }
    });
    // 文件名不重复，可以创建文档
    if (excelflag) {
        if (saveState == "my_doc") {
            $.ajax({
                url: "/saveuserExcel/",
                type: "POST",
                data: {
                    excel_name: excel_name,
                    excel_content: "",
                },
                dataType: "json",
                success: function (data) {
                    if (data.saveStatus == "success") {
                        //保存一个空的excel
                        toExcel(excel_name, data.userId, data.fileId,data.roleName)
                    }
                }
            })
        } else {
            $.ajax({
                url: "/saveTeamExcel/",
                type: "POST",
                data: {
                    excel_name: excel_name,
                    excel_content: "",
                    teamId: saveState
                },
                dataType: "json",
                success: function (data) {
                    if (data.saveStatus == "success") {
                        toExcel(excel_name,data.userId, data.fileId,data.roleName)
                    }
                }
            })
        }
    }
})

// 输入框获得焦点清除提示内容
$("#excel_name").focus(function () {
    $("#excelNameExist").text("")
});

// 关闭模态框清空文档名称
$('#createExcel').on('hide.bs.modal', function () {
    $("#excel_name").val("")
})

//打开已经存在的excel
function toExcel(excel_name, userId, fileId,roleName) {
    window.location.href = "/excelModify/?saveState=" + saveState + "&file_name=" + excel_name +
        "&user_id=" + userId + "&fileId=" + fileId  + "&roleName=" + roleName;
}

//点击保存按钮 进行数据保存

    $("#CKEditor_data_modify").on("click", function () {
        var excel_name = $("#excel_title").val();
        var fileId = $("#fileId").val()
        if (excel_name == null || excel_name == "") {
            alert("请输入文档名称");
            return;
        }
        //表格数据为二维数据
        var a=getTableData();
        //将数组转换为字符串格式
        excel_content=getExcelcontent(a)

        //将数据保存到数据库中
        $.ajax({
            type: 'POST',
            url: '/saveExcel/',
            dataType: "json",
            data:{
                excel_content: excel_content,
                excel_name: excel_name,
                fileId: fileId,
            },
            success: function (data) {
                if (data.saveStatus == "success") {
                    // 保存成功
                  alert('excel保存成功')
                } else {
                    // 保存失败
                    alert("保存失败了");
                }
            }
        })
     });
//获取表格中的数据
function getTableData() {
    var a=[];
    //var trList = $('#aa').find('tbody').children("tr");
    var trList = $("tbody").children("tr");
    for (var i = 1; i < trList.length; i++) {
        var tdArr = trList.eq(i).find("td");
        var b=[];
        for (var j = 1; j < tdArr.length; j++) {
            roiInfo = tdArr.eq(j).text();
            b[j-1]=roiInfo;
        }
        a[i-1]=b;
    }
    return a;
}
//将数组转换成字符串
function getExcelcontent(objarr) {
    var typeNO = objarr.length;
    var tree = "[";
    for (var i = 0 ;i < typeNO ; i++){
        tree += "[";
        for (var j=0;j<typeNO;j++){

            if (objarr[i][j]==""){
                  tree +="'"+ null+"',";
            }else{
                tree +="'"+ objarr[i][j]+"',";
            }
        }
        tree += "]";
            if(i<typeNO-1){
                tree+=",";
            }
    }
    tree+="]";
    return tree;
}


  // 加载时获取文档标题
    var excel_save_state = $("#excel_save_state").val();    // 文件状态 “my_doc”：个人  else：团队
    var userId = $("#userId").val();    // 用户的id
    var teamId = $("#teamId").val();    // 团队的id
    content = $("#get_excel_content").html();  // 页面加载时获取的文档内容
    fileName = $("#excel_title").val();  // 页面加载时获取的文档标题
    var fileId = $("#fileId").val()

//点击保存版本
    $("#saveedi").on("click", function () {
        if (saveState == "my_doc") {
            // 保存个人版本
            saveEdition();
        } else {
            // 保存团队的版本
            saveTeamEditor(teamId, fileId);
        }
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


//阻止浏览器默认右击点击事件
    $("#aaaa").on("contextmenu", "tr", function () {
        return false;
    });


// 保存个人版本
function saveEdition() {
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //获取当前版本内容
    var now_doc_title = $("#docs_title").val();  //取得当前文档标题
    var fileId = $("#fileId").val()

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
                        filename: now_doc_title,
                        fileId:fileId,
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
                        "<span style='display:block'>" +
                        "<span class='sspan' title='"+ data.list[i][1] + "'>"+data.list[i][1]+"保存</span><span class='sspan1'>"+
                        "<button class=\"btn0\" data-toggle=\'modal\' data-target=\'#selectModal\' onclick=\"passName('" + data.list[i][5] + "','" + updatetime + "'," + str + ")\">预览</button>" +
                        "<button class=\"btn0 reduction\"  onclick=\"getoldEdition(" + str + ")\">还原</button>" +
                        "<button class=\"btn0 del\" onclick='delectEdition(" + data.list[i][4] + ")'>删除</button></span></span>\n" +
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
                        "<span style='display:block'>" +
                        "<span class='sspan' title='"+ data.list[i][1] + "'>"+data.list[i][1]+"保存</span><span class='sspan1'>"+

                        "<button class=\"btn0\" data-toggle=\'modal\' data-target=\'#selectModal\' onclick=\"passName('" + data.list[i][6] + "','" + updatetime + "'," + str + ")\">预览</button>" +
                        "<button class=\"btn0 reduction\"  onclick=\"getoldEdition(" + str + ")\">还原</button>" +
                        "<button class=\"btn0 del\" onclick='delectEdition(" + data.list[i][5] + ")'>删除</button></span></span>\n" +
                        "</div>"
                    $("#myEditor").append(html);
                }
                if ($("#roleName").val() == '只读') {
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




