$(function() {
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

  // Handle "Copy to clipboard" of search results on main Machinery page
  var clipboard = new Clipboard('.machinery .machinery li');

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
