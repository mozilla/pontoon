/* global $ */
$(function() {
  var container = $('#main .container');

  container.on('click', '.edit-info', function(e) {
    e.preventDefault();
    var infoBox = container.find('.info');
    var content = infoBox.html();
    var textArea = $('.read-write-info textarea').val($.trim(content));
    $('.edit-info').hide();
    $('.read-only-info').hide();
    $('.read-write-info').toggleClass('hidden');
    textArea.focus();
  });

  container.on('click', '.cancel', function(e) {
    e.preventDefault();
    $('.edit-info').show();
    $('.read-only-info').show();
    $('.read-write-info').toggleClass('hidden');
    return false;
  });

  container.on('click', '.save', function(e) {
    var textArea = $('.read-write-info textarea');
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
        $('.read-write-info').toggleClass('hidden');
        $('.edit-info').show();
        $('.read-only-info').show();
        Pontoon.endLoader('Team info saved.');
      },
      error: function(request) {
        Pontoon.endLoader(request.responseText, 'error');
      }
    })
    return false;
  });

});
