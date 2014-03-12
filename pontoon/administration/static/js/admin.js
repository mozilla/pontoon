$(function() {

  // Edit project if selected from the menu
  $('.project .menu li').click(function (e) {
    e.preventDefault();
    window.location = 'admin/project/' + $(this).find('.project-name').html();
  });

});
