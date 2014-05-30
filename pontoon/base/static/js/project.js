$(function() {

  // Edit project if selected from the menu
  $('.locale .menu li').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
    window.location = $(this).find('.code').html() + '/' + $('#server').data('project');
  });

});
