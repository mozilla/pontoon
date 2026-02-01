$(function () {
  $('.project-selector .project .menu li:not(".no-match")').click(function () {
    $(this)
      .parents('.project-selector')
      .find('.project .selector')
      .html($(this).html());
  });
});
