$(function() {

  // Translate selected locale
  $('.locale .menu li').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
    window.location = $(this).find('.code').html() + '/' + $('#server').data('project');
  });

  // Switch between available locales and locales to request
  $('.locale .menu .search-wrapper > a').unbind('click.main').bind('click', function (e) {
    e.preventDefault();
  });

});
