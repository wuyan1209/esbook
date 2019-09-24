
var tableTitle = "<thead>\n" +
    "    <tr>\n" +
    "      <th style='width: 50%'>文件名</th>\n" +
    "      <th style='width: 30%'>作者</th>\n" +
    "      <th>更新时间</th>\n" +
    "    </tr>\n" +
    "  </thead>";
$('#editorEmail').on('show.bs.modal', function () {
   $("#table").html("");
   $("#table").append(tableTitle);
   var html = ' ';
    for (var i = 0; i < 5; i++) {
        html += '<td>123</td>' +
            '<td>wy</td>' +
            '<td>2019-09-20</td>' +
            '</tr>';
    }
    $("#table").append("<tbody>" + html + "</tbody>");
})