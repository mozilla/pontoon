$(function() {
  $('.locale .menu li:not(".no-match")').click(function () {
    $('.locale .selector').html($(this).html());
  });
});
