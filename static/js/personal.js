$(function () {
    // 查找用户的信息
     $.ajax({
            url: "/getUser/",
            type: "POST",
            async: false,
            dataType: "json",
            success: function (data) {
                // 填写个人信息
                var str="../static/assets/images/users/"+data.result[4];
                $(".img").attr("src",str);
            }
        })


    // 图片改变时
    $('.input').bind("change", function () {
        var res=$(".input").val()
        if(res==null||res==" "){
             $("#span").text("请选择图片");
             Time();
        }else{
            var extStart=res.lastIndexOf(".");
            var ext = res.substring(extStart, res.length).toUpperCase();
            if (ext != ".BMP" && ext != ".PNG" && ext != ".GIF" && ext != ".JPG" && ext != ".JPEG") {
                $("#span").text("图片限于png,gif,jpeg,jpg格式");
                Time();
            }else{
                /*提交表单*/
                document.form.submit();
            }
        }
    });

})
function Time() {
     window.setTimeout(function () {
        $("#span").text(" ");
    },1000);
}