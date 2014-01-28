$(function() {

  // Unhover on add hover
  $('.project .menu .add').hover(function() {
    $('.project .menu ul li').removeClass('hover');
  }, function() {});

  // Edit project if selected from the menu
  $('.project .menu li').live("click.pontoon", function (e) {
    e.preventDefault();
    $('.url').val($(this).find('.project-name').html());
    window.location = 'admin/project/' + $(this).find('.project-name').html();
  });

  // Edit or add project if URL typed and Enter pressed
  $('.url').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
    var key = e.keyCode || e.which;
    if (key === 13) { // Enter
      window.location = 'admin/project/' + $(this).val();
      return false;
    }
  });

});
