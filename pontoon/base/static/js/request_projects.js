$(function() {

  var menu = $('.project .menu'),
      localeProjects = $('#server').data('locale-projects') || Pontoon.getLocaleData('projects');

  function toggleProjects(show) {
    menu.find('li').toggleClass('limited', !show).toggle(!show)
      .find('.check').toggle(!show);

    $(localeProjects).each(function() {
      menu.find('[data-slug="' + this + '"]').parent().toggleClass('limited', show).toggle(show);
    });
  }

  function toggleButton(condition) {
    $('#request-projects').toggle(condition);
  }

  function updateSearch() {
    menu.find('input[type=search]:visible').trigger('keyup').focus();
  }

  // Show only projects available for the selected locale
  toggleProjects(true);
  updateSearch();

  // Switch between available projects and projects to request
  menu.find('.search-wrapper > a').click(function (e) {
    e.stopPropagation();
    e.preventDefault();

    $(this).toggleClass('back')
      .find('span').toggleClass('fa-plus-square fa-chevron-left');

    menu.toggleClass('request');

    toggleProjects(!$(this).is('.back'));
    toggleButton($(this).is('.back') && menu.find('.check.enabled').length > 0);
    updateSearch();
  });

  // Select projects
  menu.find('li').click(function (e) {
    if (menu.find('.search-wrapper > a').is('.back:visible')) {
      e.stopPropagation();

      $(this).find('.check').toggleClass('enabled');
      toggleButton(menu.find('.check.enabled').length > 0);
    }
  });

  // Request projects
  $('#request-projects').click(function(e) {
    e.preventDefault();
    e.stopPropagation();

    var locale = $('#server').data('locale') || Pontoon.getSelectedLocale(),
        projects = menu.find('ul .check.enabled').map(function(val, element) {
          return $(element).prev().data('slug');
        }).get();

    Pontoon.requestProject(locale, projects);
  });

});
