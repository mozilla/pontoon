$(function() {

  // Hide menus on click outside
  $('body').bind("click.main", function (e) {
    $('.menu').hide();
    $('.select').removeClass('opened');
    $('.menu li').removeClass('hover');
  });

  // Locale menu handler
  $('.locale .menu li:not(".no-match")').click(function () {
    var locale = $(this).find('.language').data('locale-code'),
        language = $('.locale .menu span.language[data-locale-code=' + locale + ']').parent().html();
    $('.locale .selector').html(language);
    $('.locale .selector').data('locale-code', locale);
  });

  // Trigger search with Enter
  $('#search input').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
    var value = $(this).val(),
        self = Pontoon;
    if (e.which === 13 && value.length > 0) {
      var code = $('.locale .selector .language').data('locale-code');
      self.locale = {
        code: code
      };
      self.getMachinery(value, "helpers", "search");
      return false;
    }
  });

});
