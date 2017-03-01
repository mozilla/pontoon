$(function() {

  // Locale menu handler
  $('.locale .menu li:not(".no-match")').click(function () {
    var locale = $(this).find('.language').data('code'),
        language = $('.locale .menu span.language[data-code=' + locale + ']').parent().html();
    $('.locale .selector').html(language);
    $('.locale .selector').data('code', locale);
  });

  // Trigger search with Enter
  $('#search input').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
    var value = $(this).val(),
        self = Pontoon;
    if (e.which === 13 && value.length > 0) {
      var code = $('.locale .selector .language').data('code');
      self.locale = {
        code: code
      };
      self.getMachinery(value, "helpers", "search");
      return false;
    }
  });

  // Handle "Copy to clipboard" on search results.
  var clipboard = new Clipboard('.search .machinery li');

  clipboard.on('success', function(event) {
    var successMessage = $('<span class="clipboard-success">Copied!</span>'),
        $trigger = $(event.trigger);

    $('.clipboard-success').remove();
    $trigger.find('header').prepend(successMessage);
    setTimeout(function() {
      successMessage.fadeOut(500, function() {
         successMessage.remove();
      });
    }, 1000);
  });
});
