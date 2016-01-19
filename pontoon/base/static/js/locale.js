$(function() {

  // Show only projects available for the selected locale
  var localeProjects = $('#server').data('locale-projects');
  $(localeProjects).each(function() {
    $('.menu [data-slug="' + this + '"]').parent().addClass('limited').show();
  });
  $('.menu:visible input[type=search]').trigger("keyup");

  // Request new project
  $('.project .menu li').click(function (e) {
    if ($('.search-wrapper > a').is('.back')) {
      e.preventDefault();

      var locale = $('#server').data('locale'),
          project = $(this).find('.name').data('slug');

      Pontoon.requestProject(locale, project);
    }
  });

  // Switch between available projects and projects to request
  $('.project .menu .search-wrapper > a').click(function (e) {
    e.preventDefault();

    var menu = $(this).parents('.menu').toggleClass('request');
    menu.find('.sort .progress, .latest').toggle();
    $(this).toggleClass('back')
      .find('span').toggleClass('fa-plus-square fa-chevron-left');

    if ($(this).is('.back')) {
      menu.find('li').addClass('limited').show();
      $(localeProjects).each(function() {
        menu.find('[data-slug="' + this + '"]').parent().removeClass('limited').hide();
      });

    } else {
      menu.find('li').removeClass('limited').hide();
      $(localeProjects).each(function() {
        menu.find('[data-slug="' + this + '"]').parent().addClass('limited').show();
      });
    }

    $('.menu:visible input[type=search]').trigger("keyup").focus();
  });

});
