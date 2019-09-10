
//ajax添加协作空间
function addTeam() {
    var teamName = $("#teamName").val();
    if (teamName == "" || teamName == null) {
        alert("空间名不能为空！")
        return false;
    }
    if (teamName.length > 50) {
        alert("空间名最长50字符！")
        return false;
    }
    $.ajax({
        url: "/addTeam/",
        type: "POST",
        dataType: "json",
        data: {
            "teamName": teamName
        },
        success: function (data) {
           if(data.status==200){
                alert(data.message);
                window.location.href='/index/';
            }else{
                alert(data.message);
            }
        },
    });
};

//修改协作空间
function editTeam() {
    var teamName = $("#name").val();
    var preTeamName = $("#perName").val();
    if (teamName == "" || teamName == null) {
        alert("空间名不能为空！");
        return false;
    }
    if (teamName.length > 50) {
        alert("空间名最长50字符！");
        return false;
    }
    if(teamName==preTeamName){
        alert("请修改");
        return false;
    }
    $.ajax({
        url: "/editTeam/",
        type: "POST",
        dataType: "json",
        data: {
            "teamName": teamName,
            "pTeamName":preTeamName,
        },
        success: function (data) {
            if(data.status==200){
                alert(data.message);
                window.location.href='/index/';
            }else{
                alert(data.message);
            }
        },
    });
};

//关闭协作空间的模态框时刷新index页面
$('#teamModal').on('hide.bs.modal', function () {
    window.location.href = '/index/';
});

//关闭修改协作空间的模态框时刷新index页面
$('#editTeam').on('hide.bs.modal', function () {
    window.location.href = '/index/';
});

//获取该成员的协作空间
$(function () {
    $.ajax({
        url: "/getAllTeam/",
        type: "POST",
        dataType: "json",
        success: function (data) {
            if (data.status == 200) {
                //给ul动态添加li
                var num = 1;
                for (i = 0; i < data.list.length; i++) {
                    html = " <div class=\"team dropdown\">\n"+
                        "<a href= \"javascript:void (0)\"  onclick=\"changeSaveState('" + data.list[i][0] + "','" + data.list[i][1] + "')\" class=\"aaaaa\">\n" +
                        "<span class=\"span1\"><i class=\"icon-search icon-home\"></i></span> \n"+
                        " <span class=\"span2\" title=' " + data.list[i][1] + " '>" + data.list[i][1] + "</span></a>\n" +
                        " <span class=\"span3\" id=\"dropdownMenu1\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"true\"><i class=\"ti-settings\" ></i></span>\n" +

                        "<ul class=\"dropdown-menu\"  aria-labelledby=\"dropdownMenu1\">\n"+
                        "<li><a data-toggle=\"modal\" data-target=\"#myModal\" class=\"dropdown-item\" onclick=\"passName1('" + data.list[i][1] + "')\" href=\"javascript:void(0)\">协作</a></li>\n" +
                        "<li><a data-toggle=\"modal\" data-target=\"#editTeam\" class=\"dropdown-item\" onclick=\"passName2('" + data.list[i][1] + "')\" href=\"javascript:void(0)\">设置</a></li>\n"+
                        "<hr style='margin-top: 0;margin-bottom: 0'/>"+
                        "<li><a class=\"dropdown-item\" style=\'color:red\' id='del'  onclick='delTeam(" + data.list[i][0] + ")'>删除</a></li>\n" +
                        "</ul>"+
                        "</div>";
                    $(".sidebar-nav").append(html);
                }
            }
        },
    });
});

//给添加协作者的模态框传参
function passName1(teamName) {
    //把协作空间名传到添加协作者的模态框里
    $("#tName").text(teamName);
    //清除用户的搜索框和搜索结果
    $("#userName").val("");
    $("#table1  tr").html("");
    //弹出模态框的时候查询普通协作者和管理员
    searchTeamUser();
    searchTeamAdmin()
};

//给修改协作空间的模态框传参
function passName2(teamName) {
    //把协作空间名传到添加协作者的模态框里
    $("#perName").val(teamName);
    $("#name").val(teamName);
};

//删除协作空间，放入回收站
function delTeam(teamId) {
     if (window.confirm("您确定要删除吗？")) {
         $.ajax({
             url: "/delTeam/",
             type: "POST",
             dataType: "json",
             data: {
                 "teamId": teamId,
             },
             success: function (data) {
                 alert(data.message);
                 window.location.href = '/index/';
             },
         });
     }

};

var title = "<span class='one' style='font-weight: 500;'>文件名</span>\n" +
        "<span class='two' style='font-weight: 500;'>删除者</span>\n" +
        "<span class='two'  style='font-weight: 500;margin-top: 15px'>删除时间</span>\n"+"<hr class='hr1'>";
//回收站
function bin() {
    saveState = "my_doc";
    $.ajax({
        url: "/myBin/",
        type: "POST",
        dataType: "json",
        data:{"page":1},
        success: function (data) {
            //处理第一页的数据
            appendBin(data);
            var options = {//根据后台返回的分页相关信息，设置插件参数
                bootstrapMajorVersion: 3, //如果是bootstrap3版本需要加此标识，并且设置包含分页内容的DOM元素为UL,如果是bootstrap2版本，则DOM包含元素是DIV
                currentPage: data.page, //当前页数
                totalPages: data.totalPage, //总页数
                numberOfPages: data.pageSize,//每页记录数
                itemTexts: function (type, page, current) {//设置分页按钮显示字体样式
                    switch (type) {
                        case "first":
                            return "首页";
                        case "prev":
                            return "上一页";
                        case "next":
                            return "下一页";
                        case "last":
                            return "末页";
                        case "page":
                            return page;
                    }
                },
                onPageClicked: function (event, originalEvent, type, page) {//分页按钮点击事件
                    $.ajax({//根据page去后台加载数据
                        url: "/myBin/",
                        type: "post",
                        dataType: "json",
                        data: {"page": page},
                        success: function (data) {
                            appendBin(data);//处理数据
                        }
                    });
                }
            };
            $('#mypage').bootstrapPaginator(options);//设置分页
        },
    })
};
function appendBin(data) {
    $("#roleName").val("超级管理员");
    var username=$("#user").text()
    /*清空之前的数据*/
    $("#tab").html("");
    $("#bin").html("");
    $("#h2").text("回收站");
    $("#bin").append(title);
    if (data.status == 2001) {
        var tmp = '<span style="margin:18px">' + data.message + '</span>';
        $("#bin").append(tmp);
        $("#Hidden").css("display", "none");
    } else {
        $("#Hidden").css("display", "block");
        for (i = 0; i < data.message.length; i++) {
            var html = " ";
            var text = data.message[i][1];
            var mystr = text.substring(0, 10) + "  " + text.substring(11);
            html += " <div class=\"dropdown\">\n"
            /*协作空间*/
            var t1 = " <span class='one' id=\"dropdownMenu\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"true\"><i class=\"icon-search icon-home\"></i>&nbsp;&nbsp;" + data.message[i][0] + "</span>\n"
            /*word*/
            var t2 = " <span class='one' id=\"dropdownMenu\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"true\"><img style='width: 17px' src='/static/assets/images/word.png'/>&nbsp;&nbsp;" + data.message[i][0] + "</span>\n"
            /*excel*/
            var t3 = " <span class='one' id=\"dropdownMenu\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"true\"><img style='width: 17px' src='/static/assets/images/excel.png'/>&nbsp;&nbsp;" + data.message[i][0] + "</span>\n"
            /*ppt*/
            var t4 = " <span class='one' id=\"dropdownMenu\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"true\"><img style='width: 17px' src='/static/assets/images/ppt.png'/>&nbsp;&nbsp;" + data.message[i][0] + "</span>\n"
            if (data.message[i][3] == '协作空间') {
                html = html + t1;
            } else if (data.message[i][3] == 0) {
                html = html + t2
            } else if (data.message[i][3] == 1) {
                html = html + t3
            } else if (data.message[i][3] == 2) {
                html = html + t4
            }
            html += " <span class='two'>" + data.message[i][4] + "</span>\n" +
                " <span class='two'>" + mystr + "</span>\n" +
                "<hr class='hr1'>" +
                "<ul class=\"dropdown-menu\"  aria-labelledby=\"dropdownMenu\">\n"
            if(username==data.message[i][4] ){
                 html+= "<li><button  class=\"dropdown-item\" " +
                "onclick = \"restore('" + data.message[i][2] + "','" + data.message[i][3] + "')\">" +
                "<img style='width: 20px;height: auto' src='/static/assets/images/undo.png'/>&nbsp;&nbsp;恢复文件</button></li>\n" +
                "<hr style='margin-top: 0;margin-bottom: 0'/>" +
                "<li><button class=\"dropdown-item\" style='color: red'  " +
                "onclick = \"deleteAll('" + data.message[i][2] + "','" + data.message[i][3] + "')\">" +
                "<span class=\"icon-search icon-trash\" style='margin-left: 2%'></span>&nbsp;&nbsp;&nbsp;彻底删除</button></li>\n"
            }else{
                  html+= "<li><button  class=\"dropdown-item\" disabled='disabled' " +
                "onclick = \"restore('" + data.message[i][2] + "','" + data.message[i][3] + "')\">" +
                "<img style='width: 20px;height: auto' src='/static/assets/images/undo.png'/>&nbsp;&nbsp;恢复文件</button></li>\n" +
                "<hr style='margin-top: 0;margin-bottom: 0'/>" +
                "<li><button disabled='disabled' class=\"dropdown-item\" style='color: red'  " +
                "onclick = \"deleteAll('" + data.message[i][2] + "','" + data.message[i][3] + "')\">" +
                "<span class=\"icon-search icon-trash\" style='margin-left: 2%'></span>&nbsp;&nbsp;&nbsp;彻底删除</button></li>\n"
            }
            html+= "</ul>" +
                "</div>";
            $("#bin").append(html);
        }
        $("#inputfiles").removeAttr("disabled")
        $("#daoru").removeAttr("disabled")
    }
}

//回收站里恢复文件
function restore(id,w) {
    $.ajax({
        url: "/restore/",
        type: "POST",
        dataType: "json",
        data:{
            "id":id,
            "what":w
        },
        success: function (data) {
            if (data.status == 200) {
                alert(data.message);
                if(w=='协作空间'){
                    window.location.href = '/index/';
                }else{
                  bin()
                }
            } else {
                alert(data.message);
            }
        },
    })
};

//回收站彻底删除文件
function deleteAll(id,w) {
     if (window.confirm("即将彻底删除 1 个文件。删除后将无法恢复，请谨慎操作！")) {
         $.ajax({
             url: "/deleteAll/",
             type: "POST",
             dataType: "json",
             data: {
                 "id": id,
                 "what": w
             },
             success: function (data) {
                 if (data.status == 200) {
                     alert(data.message);
                     bin()
                 } else {
                     alert(data.message);
                 }
             },
         })
     }

}