$(function() {

  // Edit project if selected from the menu
  $('.project .menu li').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
    window.location = 'admin/projects/' + $(this).find('.name').data('slug');
  });

});
