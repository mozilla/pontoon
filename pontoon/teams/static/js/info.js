/* global $ */
$(function() {
  var container = $('#main .container');

  container.on('click', '.edit-info', function(e) {
    e.preventDefault();
    var infoBox = container.find('.info');
    var content = infoBox.html();
    var textArea = container.find('.read-write-info textarea').val($.trim(content));
    container.find('.edit-info').hide();
    container.find('.read-only-info').hide();
    container.find('.read-write-info').toggleClass('hidden');
    textArea.focus();
  });

  container.on('click', '.cancel', function(e) {
    e.preventDefault();
    container.find('.edit-info').show();
    container.find('.read-only-info').show();
    container.find('.read-write-info').toggleClass('hidden');
    return false;
  });

  container.on('click', '.save', function(e) {
    var textArea = container.find('.read-write-info textarea');
    var content = textArea.val();
    $.ajax({
      url: textArea.parent().data('url'),
      type: 'POST',
      data: {
        csrfmiddlewaretoken: textArea.parent().data('csrf'),
        team_info: content
      },
      success: function(data) {
        container.find('.info').html(data);
        container.find('.read-write-info').toggleClass('hidden');
        container.find('.edit-info').show();
        container.find('.read-only-info').show();
        Pontoon.endLoader('Team info saved.');
      },
      error: function(request) {
        Pontoon.endLoader(request.responseText, 'error');
      }
    });
    return false;
  });

});
