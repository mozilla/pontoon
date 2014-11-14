$(function() {

  // Prevent hiding project selector on click outside
  $('body').unbind("click.main");

  // Translate selected locale
  $('.locale .menu li').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
    window.location = $(this).find('.code').html() + '/' + $('#server').data('project');
  });

});
