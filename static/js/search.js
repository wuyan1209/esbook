$(function () {
    var flag = true;
    $('#search-bar').on('compositionstart', function () {
        flag = false;
    });
    $('#search-bar').on('compositionend', function () {
        flag = true;
    });
    $('#search-bar').on('input', function () {
        var searchCondition = $(this).val();

        setTimeout(function () {
            if (flag) {
                // alert($(_this).val())
                $("#search-results").css("display", "block");
                if (searchCondition == "") {
                    $("#search-results").css("display", "none");
                }
                if (searchCondition == " " || searchCondition == null) {
                    alert("请输入要搜索的文件名或文件内容");
                    $("#search-bar").val("")
                    return;
                }
                $.ajax({
                    url: "/searchFile/",
                    type: "POST",
                    data: {searchCondition: searchCondition},
                    dataType: "json",
                    success: function (data) {
                        if (data == "" || data == null) {
                            // 未找到文件
                            $("#search-results-show").html("")
                            $("#search-results-show").append("<div class=\"search-show\">未找到该文件</div>")
                        } else {
                            // 找到文件
                            $("#search-results-show").html("")
                            for (let i = 0; i < data.length; i++) {
                                data[i].file_name = process_result(data[i].file_name, searchCondition);
                                data[i].content = process_result(data[i].content, searchCondition);
                                let html = "<li onclick='openFile(" + data[i].file_id + ")' class=\"list-group-item\">\n" +
                                    "                    <div>\n" +
                                    "                        <div>";
                                if (data[i].type == 0) {
                                    html += "<span><img src=\"/static/assets/images/802格式_文档docx.png\" width=\"20px\"\n" +
                                        "                                       height=\"20px\"></span>"
                                }
                                html += "<span>" + data[i].file_name + "</span>\n" +
                                    "                        </div>\n" +
                                    "                        <div class=\"search-show\">\n" +
                                    "                            " + data[i].content +
                                    "                        </div>\n" +
                                    "                        <div class=\"search-show\">\n" +
                                    "                            " + data[i].cre_date + " 更新\n" +
                                    "                        </div>\n" +
                                    "                    </div>\n" +
                                    "                </li>"
                                $("#search-results-show").append(html)
                            }
                        }


                    }
                })

            }
        }, 0)
    })
});

// 关闭搜索结果框
function closeSearchReasult() {
    $("#search-results").css("display", "none")
}

// 处理查询结果
function process_result(data, searchCondition) {
    data = data.replace(/<[^>]+>/g, ""); //截取html标签
    data = data.replace(/&nbsp;/ig, "");//截取空格等特殊标签
    var start = data.indexOf(data) - 10;
    if (start < 0) {
        start = 0
    }
    var end = data.indexOf(data) + 20 - start;
    data = data.substring(start, end)
    data = data.replace(searchCondition, "<mark style=\"background-color:#0af34a\">" + searchCondition + "</mark>");
    return data
}

// 点击查询结果框以外的地方关闭查询结果框
window.onload = function () {
    document.onclick = function (e) {
        var ele = e ? e.target : window.event.srcElement;
        if (ele.id !== 'search-results') {
            document.getElementById('search-results').style.display = 'none';
        }
    };
};

// 打开搜索到的文件
function openFile(fileId) {
    window.location.href = "/serachRTFdoc/?file_id="+fileId;
}
