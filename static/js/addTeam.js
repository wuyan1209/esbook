$(function ($) {

    //获取该成员的协作空间
    $.ajax({
        url: "/getAllTeam/",
        type: "POST",
        dataType: "json",
        success: function (data) {
            if (data.status == 200) {
                //给ul动态添加li
                for (i = 0; i < data.message.length; i++) {
                    html = "<li data-id=\"aaa\" class=\"waves-effect waves-dark\" >\n" +
                        " <span title=' "+data.message[i]+" 'style=\"margin-left: 0px;width: 65%;display: inline-block;word-break:keep-all;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;\">\n" +
                        " <i class=\"icon-search icon-home\"></i>&nbsp;&nbsp;" +data.message[i]+ "</span>\n" +
                        " <span style=\"margin-left: 18px;width: 20%;display: inline-block\"><i class=\"ti-settings\"></i></span>\n" +
                        "</li>"
                    $("#sidebarnav").append(html);
                }
            }
        },
    });


    //弹出窗口
    $("#demo").hover(function () {
        $(this).stop().animate({
            opacity: '1'
        }, 600);
    }, function () {
        $(this).stop().animate({
            opacity: '0.6'
        }, 1000);
    }).on('click', function () {
        $("#main-wrapper").append('<div id="mask"></div>');
        $("#mask").addClass("mask").fadeIn("slow");
        $("#LoginBox").fadeIn("slow");
    });

    //关闭弹窗
    $(".cancel").hover(function () {
        $(this).css({color: 'black'})
    }, function () {
        $(this).css({color: '#999'})
    }).on('click', function () {
        $("#LoginBox").fadeOut("fast");
        $("#mask").css({display: 'none'});
    });

    //ajax添加协作空间
    $("#loginbtn").click(function () {
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
                "teamName": $("#teamName").val(),
            },
            success: function (data) {
                if (data.status == 200) {
                    //跳转到主页面
                    alert(data.message);
                    window.location.href = '/index/';
                } else {
                    alert(data.message);
                }
            },
        });
    });
});