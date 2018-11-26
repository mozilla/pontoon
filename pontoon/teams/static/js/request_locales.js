/* Public functions used across different files */
var Pontoon = (function (my) {
  return $.extend(true, my, {
    requestTeams: {

      /*
       * Toggle available teams
       *
       * show request team form
       */
      toggleTeams: function (show) {

        // Toggle
        $('.controls .request-toggle')
          .toggleClass('back', !show)
          .find('span')
            .toggleClass('fa-chevron-right', show)
            .toggleClass('fa-chevron-left', !show);

        // Hide all teams
        $('.team-list').toggle(show);

        // Show team form
        $('#request-team-form').toggle(!show);

        $('.controls input[type=search]:visible').trigger('input');
        Pontoon.requestTeams.toggleButton(!show);
      },

      /*
       * Toggle request team button
       */
      toggleButton: function (condition) {
        condition = condition || true;
        var show = condition  &&
          ($.trim($('#request-team-form #id_name').val()) !== '') &&
          ($.trim($('#request-team-form #id_code').val()) !== '') ;
        $('#request-team-note').toggle(show);
        $('#request-team').toggle(show);
      },

      /*
       * Request team to be added to Pontoon
       */
      request: function(name, code) {
        $.ajax({
          url: '/request/team/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            name: name,
            code: code
          },
          success: function() {
            Pontoon.endLoader("New team request sent.", '', 5000);
          },
          error: function() {
            Pontoon.endLoader('Oops, something went wrong.', 'error');
          },
          complete: function() {
            $('#request-team-form #id_name').val('');
            $('#request-team-form #id_code').val('');
            Pontoon.requestTeams.toggleButton(true);
            window.scrollTo(0, 0);
          }
        });
      }

    }
  });
}(Pontoon || {}));

$(function() {
  var container = $('#main .container');

  // Switch between available teams and teams to request
  container.on('click', '.controls .request-toggle', function (e) {
    e.stopPropagation();
    e.preventDefault();

    Pontoon.requestTeams.toggleTeams($(this).is('.back'));
  });

  // Enter team details
  container.on('keyup', '#request-team-form input[type=text]', function (e) {
    if ($('.controls .request-toggle').is('.back:visible')) {
      e.stopPropagation();
      Pontoon.requestTeams.toggleButton();
    }
  });


  // Request team
  container.on('click', '#request-team', function(e) {
    e.preventDefault();
    e.stopPropagation();

    var name = $.trim($('#request-team-form #id_name').val());
    var code = $.trim($('#request-team-form #id_code').val())

    if ($(this).is('.confirmed')) {
      Pontoon.requestTeams.request(name, code);
      $(this)
        .removeClass('confirmed')
        .html('Request new team');
    } else {
      $(this)
        .addClass('confirmed')
        .html('Are you sure?');
    }
  });

});
