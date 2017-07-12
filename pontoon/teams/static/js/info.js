/* global $ */
$(function() {
  var container = $('#main .container');

  container.on('click', '.edit-info', function(e) {
    e.preventDefault();
    var infobox = $(".info");
    var content = infobox.html();
    var text_area = $(".editable-info textarea").val(content);
    $(".edit-info").hide();
    $(".read-only-info").hide();
    $(".editable-info").toggleClass("hidden");
    text_area.focus();
    return false;
  });
  container.on('click', '.save.info', function(e) {
    var text_area = $(".editable-info textarea");
    var content = text_area.val();
    $.ajax({
      url: text_area.parent().data('url'),
      method: 'POST',
      beforeSend: function(xhr) {
        xhr.setRequestHeader("X-CSRFToken", text_area.parent().data('csrf'));
      },
      data: content,
      dataType: "text",
    })
      .done(function(jqXHR) {
        $(".info").html(jqXHR.responseText);
        $(".editable-info").toggleClass("hidden");
        $(".edit-info").show();
        $(".read-only-info").show();
      })
      .fail(function(jqXHR) {
        $(".editable-info textarea").val(jqXHR.responseText);
      });
  });
});
