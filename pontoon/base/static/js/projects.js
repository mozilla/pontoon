$(function() {

  // Show selected project locales
  $('.project .menu li').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
    window.location = '/projects/' + $(this).find('.name').data('slug');
  });

});
