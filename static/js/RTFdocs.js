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
    // 使用Ajax技术将文档名称和文档内容保存到数据库中
    $("#CKEditor_data_save").on("click", function () {
        saveDocs()
    });

    // ctrl+s 保存
    $("#editor").keydown(function (e) {
            if (e.keyCode == 83 && e.ctrlKey ){
                e.preventDefault();
                saveDocs();
            }
        })

    //使用ajax将文档从数据库中读取出来

})

// 保存文档
function saveDocs() {
    var doc_content = document.getElementById("editor"); //取得纯文本
    doc_content = doc_content.innerHTML;    //取得html格式的内容
    var doc_title = $("#docs_title").val();  //取得文档标题

    $.ajax({
        type: 'POST',
        url: '/saveDocTest/',
        dataType: "json",
        data: {
            doc_content: doc_content,
            doc_title: doc_title
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