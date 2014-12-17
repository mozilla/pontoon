$(function() {

  // Show only locales available for the selected project
  var projectLocales = $('#server').data('project-locales');
  $(projectLocales).each(function() {
    $('.menu').find('.language.' + this).parent().addClass('limited').show();
  });
  $('.menu:visible input[type=search]').trigger("keyup");

  // Locale menu handler
  $('.locale .menu li').click(function (e) {
    e.preventDefault();

    // Request new locale
    if ($('.locale .menu .search-wrapper > a').is('.back')) {
      var locale = $(this).find('.language').attr('class').split(' ')[1],
          project = $('#server').data('project');
      Pontoon.requestLocale(locale, project);

    // Translate locale
    } else {
      window.location = $(this)
        .find('.code').html() + '/' + $('#server').data('project');
    }
  });

  // Switch between available locales and locales to request
  $('.locale .menu .search-wrapper > a').click(function (e) {
    e.preventDefault();

    var menu = $(this).parents('.menu');
    menu.find('.sort span:eq(2)').toggle();
    $(this).toggleClass('back')
      .find('span').toggleClass('fa-plus-square fa-chevron-left');

    if ($(this).is('.back')) {
      menu.find('li').addClass('limited').show();
      $(projectLocales).each(function() {
        menu.find('.language.' + this).parent().removeClass('limited').hide();
      });

    } else {
      menu.find('li').removeClass('limited').hide();
      $(projectLocales).each(function() {
        menu.find('.language.' + this).parent().addClass('limited').show();
      });
    }

    $('.menu:visible input[type=search]').trigger("keyup").focus();
  });

});
