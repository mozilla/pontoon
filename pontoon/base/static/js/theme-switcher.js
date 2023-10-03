$(function () {
  $('.appearance .toggle-button button').click(function (e) {
    e.preventDefault();

    var self = $(this);

    // If the clicked button is already active, do nothing
    if (self.is('.active')) {
      return;
    }

    var theme = self.attr('class').split(' ')[0]; // gets the theme (dark, light, system) based on the button's class

    $.ajax({
      url: '/api/v1/user/theme/' + $('#server').data('username') + '/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        theme: theme,
      },
      success: function () {
        $('.appearance .toggle-button button').removeClass('active');

        self.addClass('active');

        $('body')
          .removeClass('dark-theme light-theme system-theme')
          .addClass(`${theme}-theme`);

        Pontoon.endLoader(`Theme changed to ${theme}.`);
      },
      error: function (request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      },
    });
  });
});
