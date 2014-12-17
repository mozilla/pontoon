$(function() {

  // Show selected project locales
  $('.project .menu li').click(function (e) {
    e.preventDefault();
    window.location = '/projects/' + $(this).find('.name').data('slug');
  });

});
