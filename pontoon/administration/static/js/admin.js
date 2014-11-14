$(function() {

  // Prevent hiding project selector on click outside
  $('body').unbind("click.main");

  // Edit project if selected from the menu
  $('.project .menu li').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
    window.location = 'admin/project/' + $(this).find('.project-name').data('slug');
  });

});
