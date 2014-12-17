$(function() {

  // Edit project if selected from the menu
  $('.project .menu li').click(function (e) {
    e.preventDefault();
    window.location = 'admin/projects/' + $(this).find('.name').data('slug');
  });

});
