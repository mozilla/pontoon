$(function () {
  function getSystemTheme() {
    if (
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      return 'dark';
    } else {
      return 'light';
    }
  }

  function updateTheme(newTheme) {
    if (newTheme === 'system') {
      newTheme = getSystemTheme();
    }
    $('body')
      .removeClass('dark-theme light-theme system-theme')
      .addClass(`${newTheme}-theme`);

    if (newTheme !== 'system') {
      Pontoon.endLoader(`Theme changed to ${newTheme}.`);
    }
  }

  window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', function (e) {
      if ($('.appearance .toggle-button button.system').hasClass('active')) {
        if (e.matches) {
          updateTheme('dark');
        } else {
          updateTheme('light');
        }
      }
    });

  $(document).ready(function () {
    if ($('body').hasClass('system-theme')) {
      let systemTheme = getSystemTheme();
      $('body').removeClass('system-theme').addClass(`${systemTheme}-theme`);
    }
  });

  $('.appearance .toggle-button button').click(function (e) {
    e.preventDefault();

    var self = $(this);

    if (self.is('.active')) {
      return;
    }

    var theme = self.attr('class').split(' ')[0];

    $.ajax({
      url: '/api/v1/user/' + $('#server').data('username') + '/theme/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        theme: theme,
      },
      success: function () {
        $('.appearance .toggle-button button').removeClass('active');
        self.addClass('active');
        updateTheme(theme);
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
