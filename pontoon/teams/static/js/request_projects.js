/* Public functions used across different files */
var Pontoon = (function (my) {
  return $.extend(true, my, {
    requestProjects: {

      /*
       * Toggle available projects and projects to request
       *
       * show Show enabled projects?
       */
      toggleProjects: function (show) {
        var localeProjects = $('#server').data('locale-projects');

        // Toggle
        $('.controls .request-toggle')
          .toggleClass('back', !show)
          .find('span')
            .toggleClass('fa-chevron-right', show)
            .toggleClass('fa-chevron-left', !show);

        // Hide all projects
        $('.projects')
          .toggleClass('request', !show)
          .find('tbody tr')
            .toggleClass('limited', !show)
            .toggle(!show);

        // Show requested projects
        $(localeProjects).each(function() {
          $('.projects')
              .find('td[data-slug="' + this + '"]')
            .parent()
              .toggleClass('limited', show)
              .toggle(show);
        });

        $('.controls input[type=search]:visible').trigger('input');
        Pontoon.requestProjects.toggleButton(!show);
      },

      /*
       * Toggle request projects button
       */
      toggleButton: function (condition) {
        condition = condition || true;
        var show = condition && $('.projects td.check.enabled:visible').length > 0;

        $('#request-projects-note').toggle(show);
        $('#request-projects').toggle(show);
      },

      /*
       * Request project to be added to locale
       *
       * locale Locale code
       * projects Array of Project slugs
       */
      request: function(locale, projects) {
        $.ajax({
          url: '/teams/' + locale + '/request/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            projects: projects
          },
          success: function() {
            Pontoon.endLoader("New projects request sent.", '', 5000);
          },
          error: function() {
            Pontoon.endLoader('Oops, something went wrong.', 'error');
          },
          complete: function() {
            $('.projects td.check').removeClass('enabled');
            Pontoon.requestProjects.toggleProjects(true);
            window.scrollTo(0, 0);
          }
        });
      }

    }
  });
}(Pontoon || {}));

$(function() {
  var container = $('#main .container');

  // Switch between available projects and projects to request
  container.on('click', '.controls .request-toggle', function (e) {
    e.stopPropagation();
    e.preventDefault();

    Pontoon.requestProjects.toggleProjects($(this).is('.back'));
  });

  // Select projects
  container.on('click', '.projects td.check', function (e) {
    if ($('.controls .request-toggle').is('.back:visible')) {
      e.stopPropagation();

      $(this).toggleClass('enabled');
      Pontoon.requestProjects.toggleButton();
    }
  });

  // Prevent openning project page from the request panel
  var menu = container.find('.project .menu');
  menu.find('a').click(function (e) {
    if (menu.find('.search-wrapper > a').is('.back:visible')) {
      e.preventDefault();
    }
  });

  // Request projects
  container.on('click', '#request-projects', function(e) {
    e.preventDefault();
    e.stopPropagation();

    var locale = $('#server').data('locale') || Pontoon.getSelectedLocale(),
        projects = $('.projects td.check.enabled').map(function(val, element) {
          return $(element).siblings('.name').data('slug');
        }).get();

    if ($(this).is('.confirmed')) {
      Pontoon.requestProjects.request(locale, projects);
      $(this)
        .removeClass('confirmed')
        .html('Request new projects');
    } else {
      $(this)
        .addClass('confirmed')
        .html('Are you sure?');
    }
  });

});
