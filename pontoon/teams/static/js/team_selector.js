$(function() {
  $('.locale-selector .locale .menu li:not(".no-match")').click(function () {
    if ($(this).closest('#homepage').length == 1) {
      $('#homepage .locale .selector').html($(this).html());
    }
    if ($(this).closest('#preferred-locale').length == 1) {
      $('#preferred-locale .locale .selector').html($(this).html());
    }
  });
});
