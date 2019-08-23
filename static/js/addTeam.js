
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
                        " <span class=\"span2\" title=' " + data.list[i][1] + " 'style=\"word-break:keep-all;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;\">" + data.list[i][1] + "</span></a>\n" +
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

//回收站
function bin() {
    var title = "<span class='one' style='font-weight: 500;margin-top: 15px'>文件名</span>\n" +
        "<span class='two'  style='font-weight: 500;margin-top: 15px'>删除时间</span>\n"+"<hr class='hr1'>";
    $.ajax({
        url: "/myBin/",
        type: "POST",
        dataType: "json",
        success: function (data) {
            /*清空之前的数据*/
            $("#tab").html("");
            $("#bin").html("");
            $("#h2").text("回收站");
            $("#bin").append(title);
            for (i = 0; i < data.message.length; i++) {
                var text = data.message[i][1];
                var mystr = text.substring(0, 10) + "  " + text.substring(11);
                html = " <div class=\"dropdown\">\n" +
                    " <span class='one' id=\"dropdownMenu\" data-toggle=\"dropdown\" aria-haspopup=\"true\" aria-expanded=\"true\">" + data.message[i][0] + "</span>\n" +
                    " <span class='two'>" + mystr + "</span>\n" +
                    "<hr class='hr1'>"+
                    "<ul class=\"dropdown-menu\"  aria-labelledby=\"dropdownMenu\">\n" +
                    "<li><a  class=\"dropdown-item\" href=\"javascript:void(0)\" " +
                    "onclick = \"restore('" + data.message[i][2] + "','"+ data.message[i][3] + "')\">" +
                    "<img style='width: 20px;height: auto' src='/static/assets/images/undo.png'/>&nbsp;&nbsp;恢复文件</a></li>\n" +
                    "<hr style='margin-top: 0;margin-bottom: 0'/>"+
                    "<li><a  class=\"dropdown-item\" style='color: red' href=\"javascript:void(0)\" " +
                     "onclick = \"deleteAll('" + data.message[i][2] + "','"+ data.message[i][3] + "')\">" +
                    "<span class=\"icon-search icon-trash\" style='margin-left: 2%'></span>&nbsp;&nbsp;&nbsp;彻底删除</a></li>\n" +
                    "</ul>" +
                    "</div>";
                $("#bin").append(html);
            }
        },
    })
};

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
                window.location.href = '/index/';
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
                     window.location.href = '/index/';
                 } else {
                     alert(data.message);
                 }
             },
         })
     }

}