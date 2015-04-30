$(function() {

  // Hide menus on click outside
  $('body').bind("click.main", function (e) {
    $('.menu').hide();
    $('.select').removeClass('opened');
    $('.menu li').removeClass('hover');
  });

  // Locale menu handler
  $('.locale .menu li:not(".no-match")').click(function () {
    var locale = $(this).find('.language').attr('class').split(' ')[1],
        // Escape special characters in CSS notation
        code = locale.replace( /(:|\.|\[|@|\])/g, "\\$1" ),
        language = $('.locale .menu .language.' + code).parent().html();

    $('.locale .selector').html(language);
  });

  // Trigger search with Enter
  $('#search input').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
    var value = $(this).val(),
        self = Pontoon;
    if (e.which === 13 && value.length > 0) {
      self.locale = {
        code: $('.locale .selector .language').attr('class').split(' ')[1]
      };
      self.getMachinery(value, "helpers", "search");
      return false;
    }
  });

});
