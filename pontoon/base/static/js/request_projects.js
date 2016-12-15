/* Public functions used across different files */
var Pontoon = (function (my) {
  return $.extend(true, my, {
    requestProjects: {

      /*
       * Toggle available projects and projects to request
       *
       * show Show available projects?
       */
      toggleProjects: function (show) {
        var menu = $('.project .menu'),
            localeProjects = $('#server').data('locale-projects') || Pontoon.getLocaleData('projects');

        menu.toggleClass('request', !show)
          .find('.search-wrapper > a').toggleClass('back', !show)
            .find('span').toggleClass('fa-plus-square', show).toggleClass('fa-chevron-left', !show).end()
          .end()
          .find('li').toggleClass('limited', !show).toggle(!show)
            .find('.check').toggle(!show);

        $(localeProjects).each(function() {
          menu
              .find('[data-slug="' + this + '"]')
            .parent().toggleClass('limited', show).toggle(show);
        });

        menu.find('input[type=search]:visible').trigger('input').focus();
        Pontoon.requestProjects.toggleButton(!show);
      },

      /*
       * Toggle request projects button
       */
      toggleButton: function (condition) {
        var condition = condition || true,
            show = condition && $('.project .menu .check.enabled:visible').length > 0;

        $('#request-projects').toggle(show);
      },

      /*
       * Request project to be added to locale
       *
       * locale Locale code
       * projects Array of Project slugs
       */
      request: function(locale, projects) {
        Pontoon.startLoader();

        $.ajax({
          url: '/teams/' + locale + '/request/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            projects: projects
          },
          success: function(data) {
            Pontoon.endLoader(
              "New projects requested. We'll send you an email once they get enabled.", "", true);
          },
          error: function() {
            Pontoon.endLoader('Oops, something went wrong.', 'error');
          },
          complete: function() {
            $('.notification').addClass('left');
            $('.project')
              .find('.menu')
                .find('.check').removeClass('enabled').end()
                .find('.search-wrapper > a').click().end()
              .end()
              .find('.selector').click();
            window.scrollTo(0, 0);
          }
        });
      }

    }
  });
}(Pontoon || {}));

$(function() {

  var menu = $('.project .menu');

  // Switch between available projects and projects to request
  menu.find('.search-wrapper > a').click(function (e) {
    e.stopPropagation();
    e.preventDefault();

    Pontoon.requestProjects.toggleProjects($(this).is('.back'));
  });

  // Select projects
  menu.find('li').click(function (e) {
    if (menu.find('.search-wrapper > a').is('.back:visible')) {
      e.stopPropagation();

      $(this).find('.check').toggleClass('enabled');
      Pontoon.requestProjects.toggleButton();
    }
  });

  // Prevent openning project page from the request panel
  menu.find('a').click(function (e) {
    if (menu.find('.search-wrapper > a').is('.back:visible')) {
      e.preventDefault();
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

    Pontoon.requestProjects.request(locale, projects);
  });

});
