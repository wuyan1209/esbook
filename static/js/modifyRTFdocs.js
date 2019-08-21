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
    var old_doc_title = $("#docs_title").val();

    // 点击保存按钮吧保存
    $("#CKEditor_data_modify").on("click", function () {
        modifyDocs(old_doc_title);
    });
    //点击保存版本
    $("#saveedi").on("click", function () {
        saveEdition(old_doc_title);
    });

    // ctrl+s 保存
    $("#editor").keydown(function (e) {
        if (e.keyCode == 83 && e.ctrlKey) {
            e.preventDefault();
            saveDocs(old_doc_title);
        }
    });

    // 修改文档名称不能重复
    $("#docs_title").change(function () {
        var docsName = $(this).val();

        $.ajax({
            url: '/docNameExist/',
            type: 'post',
            data: {docsName: docsName},
            dataType: 'json',
            success: function (data) {
                if (data.Exist == "YES") {
                    alert("文档名字不能重复，请重新填写")
                }
            }
        })
    });
});

doc_content();

// 回显数据
function doc_content() {
    /* document.getElementById("get_doc_content"); //取得纯文本

      doc_content = doc_content.innerHTML;    //取得html格式的内容
      alert(doc_content)*/
    var doc_content = $("#get_doc_content").val()
    $("#editor").html("");
    $("#editor").html(doc_content);
}

// 打开已存在文档
function docs_modify(name, id) {
    $.ajax({
        url: '/docsModify/',
        type: 'post',
        data: {file_name: name, user_id: id},
        dataType: 'json',
        success: function (data) {
            if (data.data == "success") {
                alert("跳转链接")
                window.location.href = "/modifyRTFdocs/";
                //?file_name=" + data.file_name + "doc_content=" + data.doc_content;
            }
        }
    });
}

// 保存文档
function modifyDocs(old_doc_title) {
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //取得html格式的内容
    var now_doc_title = $("#docs_title").val();  //取得文档标题

    $.ajax({
        type: 'POST',
        url: '/ajax_modify_RTFdoc/',
        dataType: "json",
        data: {
            doc_content: doc_content,
            now_doc_title: now_doc_title,
            old_doc_title: old_doc_title
        },
        success: function (data) {
            if (data.saveStatus == "success") {
                // 保存成功
                alert("保存成功了");
            } else {
                // 保存失败
                alert("保存失败了");
            }
        }
    })
}

// 保存版本
function saveEdition(old_doc_title) {
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //取得html格式的内容
    var now_doc_title = $("#docs_title").val();  //取得文档标题

    $.ajax({
        type: 'POST',
        url: '/saveEdition/',
        dataType: "json",
        data: {
            content: doc_content,
            filename:now_doc_title
        },
        success: function (data) {
            if (data.status==200) {
                // 保存成功
                alert("保存成功了");
            } else {
                // 保存失败
                alert("保存失败了");
            }
        }
    })
}