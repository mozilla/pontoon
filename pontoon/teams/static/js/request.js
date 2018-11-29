var Pontoon = (function (my) {
  return $.extend(true, my, {
    requestItem: {
      /*
       * Toggle available projects/teams and request div
       *
       * show Show enabled projects/teams?
       */
      toggleItem: function (show, type) {
        // Toggle
        $('.controls .request-toggle')
          .toggleClass('back', !show)
          .find('span')
            .toggleClass('fa-chevron-right', show)
            .toggleClass('fa-chevron-left', !show);

        if (type === 'projects') {
          var localeProjects = $('#server').data('locale-projects');
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
          Pontoon.requestItem.toggleButton(!show, 'projects');
        }
        else if (type === 'team') {
          // Hide all teams and search bar
          $('.team-list').toggle(show);
          $('.search-wrapper').toggle(show);
          // Show team form
          $('#request-team-form').toggle(!show);
          Pontoon.requestItem.toggleButton(!show, 'team');
        }

        $('.controls input[type=search]:visible').trigger('input');
      },

      toggleButton: function (condition, type) {
        condition = condition || true;
        var show = condition
        if (type === 'projects') {
          show = condition && $('.projects td.check.enabled:visible').length > 0;
        }
        else if (type === 'team') {
          show = condition &&
          ($.trim($('#request-team-form #id_name').val()) !== '') &&
          ($.trim($('#request-team-form #id_code').val()) !== '');
        }

        $('#request-item-note').toggle(show);
        $('#request-item').toggle(show);
      },

      requestProjects: function(locale, projects) {
        $.ajax({
          url: '/' + locale + '/request/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            projects: projects,
          },
          success: function() {
            Pontoon.endLoader('New projects request sent.', '', 5000);
          },
          error: function() {
            Pontoon.endLoader('Oops, something went wrong.', 'error');
          },
          complete: function() {
            $('.projects td.check').removeClass('enabled');
            Pontoon.requestItem.toggleItem(true, 'projects');
            window.scrollTo(0, 0);
          }
        });
      },

      requestTeam: function(name, code) {
        $.ajax({
          url: '/teams/request/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            name: name,
            code: code,
          },
          success: function() {
            Pontoon.endLoader('New team request sent.', '', 5000);
          },
          error: function(res) {
            if (res.responseText === 'This team already exists.') {
              Pontoon.endLoader('This team already exists.', 'error');
            }
            else {
              Pontoon.endLoader('Oops, something went wrong.', 'error');
            }
          },
          complete: function() {
            $('#request-team-form #id_name').val('');
            $('#request-team-form #id_code').val('');
            Pontoon.requestItem.toggleButton(true, 'team');
            window.scrollTo(0, 0);
          }
        });
      }
    }
  });
}(Pontoon || {}));

$(function() {
  var container = $('#main .container');
  var type = $('#server').data('locale') ? 'projects' : 'team';

  // Switch between available projects/teams and projects/team to request
  container.on('click', '.controls .request-toggle', function (e) {
    e.stopPropagation();
    e.preventDefault();

    Pontoon.requestItem.toggleItem($(this).is('.back'), type);
  });

  // Select projects
  container.on('click', '.projects td.check', function (e) {
    if ($('.controls .request-toggle').is('.back:visible')) {
      e.stopPropagation();

      $(this).toggleClass('enabled');
      Pontoon.requestItem.toggleButton(true, type='projects');
    }
  });

  // Prevent openning project page from the request panel
  var menu = container.find('.project .menu');
  menu.find('a').click(function (e) {
    if (menu.find('.search-wrapper > a').is('.back:visible')) {
      e.preventDefault();
    }
  });

  // Enter team details
  container.on('change keyup click', '#request-team-form input[type=text]', function (e) {
    if ($('.controls .request-toggle').is('.back:visible')) {
      e.stopPropagation();
      Pontoon.requestItem.toggleButton(true, type='team');
    }
  });

  // Request projects/team
  container.on('click', '#request-item', function(e) {
    e.preventDefault();
    e.stopPropagation();

    if ($(this).is('.confirmed')) {
      if (type === 'projects') {
        var locale = $('#server').data('locale') || Pontoon.getSelectedLocale();
        var projects = $('.projects td.check.enabled').map(function(val, element) {
          return $(element).siblings('.name').data('slug');
        }).get();
        Pontoon.requestItem.requestProjects(locale, projects);
        $(this)
          .removeClass('confirmed')
          .html('Request new projects');
      }
      else if (type === 'team') {
        var name = $.trim($('#request-team-form #id_name').val());
        var code = $.trim($('#request-team-form #id_code').val());
        Pontoon.requestItem.requestTeam(name, code);
        $(this)
          .removeClass('confirmed')
          .html('Request new team');
      }
    }
    else {
      $(this)
        .addClass('confirmed')
        .html('Are you sure?');
    }
  });

});
