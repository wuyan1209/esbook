
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
            if (data.status == 200) {
                //清除input框的值
                $("#teamName").val("");
                alert(data.message);
                //window.location.href = '/index/';
            } else {
                $("#teamName").val("");
                alert(data.message);
            }
        },
    });
};

//关闭协作空间的模态框时刷新index页面
$('#teamModal').on('hide.bs.modal', function () {
    window.location.href = '/index/';
})

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
                    html = " <div class=\"team\">\n" +
                        " <a href=\"/filelist/\" class=\"aaaaa\">\n" +
                        "<span class=\"span1\"><i class=\"icon-search icon-home\"></i></span> \n" +
                        " <span class=\"span2\" title=' " + data.list[i][1] + " 'style=\"word-break:keep-all;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;\">" + data.list[i][1] + "</span></a>\n" +
                        " <span class=\"span3\"><i class=\"ti-settings\" ></i></span></div>\n" +

                        "<div class=\"teamset\" id=\"drop_down" + (i + 1) + "\">\n" +
                        "<a data-toggle=\"modal\" data-target=\"#myModal\" class=\"dropdown-item\" onclick=\"passName('" + data.list[i][1] + "')\" href=\"javascript:void(0)\">协作</a>\n" +
                        "<a class=\"dropdown-item\" href=\"#\">设置</a>\n" +
                        "<div class=\"dropdown-divider\"></div>\n" +
                        "<a class=\"dropdown-item\" style=\'color:red\' id='del'  onclick='delTeam(" + data.list[i][0] + ")'>删除</a>\n" +
                        "</div>"
                    $(".sidebar-nav").append(html);
                }
            }
        },
    });
});

//给添加协作者的模态框传参
function passName(teamName) {
    //把协作空间名传到添加协作者的模态框里
    $("#tName").text(teamName);
    //清除用户的搜索框和搜索结果
    $("#userName").val("");
    $("#table1  tr").html("");
    //弹出模态框的时候查询普通协作者和管理员
    searchTeamUser();
    searchTeamAdmin()
}

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

}
