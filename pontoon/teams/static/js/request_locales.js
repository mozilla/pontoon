/* Public functions used across different files */
var Pontoon = (function (my) {
  return $.extend(true, my, {
    requestLocales: {

      /*
       * Toggle available locales
       *
       * show request locale form
       */
      toggleLocales: function (show) {

        // Toggle
        $('.controls .request-toggle')
          .toggleClass('back', !show)
          .find('span')
            .toggleClass('fa-chevron-right', show)
            .toggleClass('fa-chevron-left', !show);

        // Hide all teams
        $('.team-list').toggle(show);

        // Show locale form
        $('#request-locale-form').toggle(!show);

        $('.controls input[type=search]:visible').trigger('input');
        Pontoon.requestLocales.toggleButton(!show);
      },

      /*
       * Toggle request locale button
       */
      toggleButton: function (condition) {
        condition = condition || true;
        var show = condition  &&
          ($.trim($('#request-locale-form #id_name').val()) !== '') &&
          ($.trim($('#request-locale-form #id_code').val()) !== '') ;
        $('#request-locales-note').toggle(show);
        $('#request-locales').toggle(show);
      },

      /*
       * Request locale to be added to Pontoon
       */
      request: function(name, code) {
        $.ajax({
          url: '/teams/requestlocale/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            name: name,
            code: code
          },
          success: function() {
            Pontoon.endLoader("New projects request sent.", '', 5000);
          },
          error: function() {
            Pontoon.endLoader('Oops, something went wrong.', 'error');
          },
          complete: function() {
            $('#request-locale-form #id_name').val('');
            $('#request-locale-form #id_code').val('');
            Pontoon.requestProjects.toggleButton(true);
            window.scrollTo(0, 0);
          }
        });
      }

    }
  });
}(Pontoon || {}));

$(function() {
  var container = $('#main .container');

  // Switch between available locales and locales to request
  container.on('click', '.controls .request-toggle', function (e) {
    e.stopPropagation();
    e.preventDefault();

    Pontoon.requestLocales.toggleLocales($(this).is('.back'));
  });

  // Enter locale details
  container.on('keyup', '#request-locale-form input[type=text]', function (e) {
    if ($('.controls .request-toggle').is('.back:visible')) {
      e.stopPropagation();
      Pontoon.requestLocales.toggleButton();
    }
  });


  // Request locale
  container.on('click', '#request-locales', function(e) {
    e.preventDefault();
    e.stopPropagation();

    var name = $.trim($('#request-locale-form #id_name').val());
    var code = $.trim($('#request-locale-form #id_code').val())

    if ($(this).is('.confirmed')) {
      Pontoon.requestLocales.request(name, code);
      $(this)
        .removeClass('confirmed')
        .html('Request new locale');
    } else {
      $(this)
        .addClass('confirmed')
        .html('Are you sure?');
    }
  });

});
