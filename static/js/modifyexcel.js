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
                        sendWebsocket(saveState, data.fileId)
                        toExcel(excel_name, 0, data.fileId,data.roleName)
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
        console.log(excel_content)
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
