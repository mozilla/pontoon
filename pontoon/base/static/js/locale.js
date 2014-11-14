$(function() {

  // Prevent hiding project selector on click outside
  $('body').unbind("click.main");

  // Translate selected project
  $('.project .menu li').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
    window.location = $('#server').data('locale') + '/' + $(this).find('.project-name').data('slug');
  });

});
