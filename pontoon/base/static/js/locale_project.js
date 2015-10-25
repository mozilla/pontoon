$(function() {
  // Remove default Enter handler
  $('.part .menu .search-project input[type=search]').off('keyup.search');

  // Search entire project with Enter
  $('form.search-form').submit(function(e) {
    var action = 'search/',
        keyword = $(this).find('[type="search"]').val();

      if ($('.locale .selector .language').length) {
        var locale = $('.locale .selector .language').attr('class').split(' ')[1],
            project = $('.project .selector .title').data('slug'),
            action = '/' + locale + '/' + project + '/' + action;
      }

      // At least one non case-sensitive option must be selected
      if ($('.options :checked').length > 1 || ($('.options :checked').length && !$('.options [name=casesensitive]:checked').length)) {
        $(this).attr('action', action);
        return;
      }


    return false;
  });

  // Focus search field when switching tabs
  $(".tabs nav a").click(function (e) {
    $('.part .menu input[type=search]:visible').trigger("keyup").focus();
  });

  // If showing search results, show search pane by default
  var search = window.location.search,
      tab = 'resources';
  if (search) {
    tab = 'search-project';
  }
  $('.part .menu nav a[href=#' + tab + ']').click();

  // Select options
  $('.search-project .options li').click(function() {
    $(this).toggleClass('enabled');
    var checkbox = $(this).find("input[type=checkbox]");
    checkbox.prop("checked", !checkbox.prop("checked"));
  });

});
