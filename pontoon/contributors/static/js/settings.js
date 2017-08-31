$(function(){

  // Locale menu handler
  $('.locale .menu li:not(".no-match")').click(function () {
    var locale = $(this).find('.language').data('code'),
        language = $('.locale .menu span.language[data-code="' + locale + '"]').parent().html();
    $('.locale .selector').html(language);
    $('.locale .selector').data('code', locale);
  });
});