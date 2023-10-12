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

  function applyTheme(newTheme) {
    if (newTheme === 'system') {
      newTheme = getSystemTheme();
    }
    $('body')
      .removeClass('dark-theme light-theme system-theme')
      .addClass(`${newTheme}-theme`);
  }

  window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', function (e) {
      // Check the 'data-theme' attribute on the body element
      let userThemeSetting = $('body').data('theme');

      if (userThemeSetting === 'system') {
        // Apply the system theme based on current system settings
        if (e.matches) {
          applyTheme('dark');
        } else {
          applyTheme('light');
        }
      }
    });

  if ($('body').hasClass('system-theme')) {
    let systemTheme = getSystemTheme();
    $('body').removeClass('system-theme').addClass(`${systemTheme}-theme`);
  }

  $('.appearance .toggle-button button').click(function (e) {
    e.preventDefault();

    var self = $(this);

    if (self.is('.active')) {
      return;
    }

    var theme = self.val();

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
        applyTheme(theme);

        // Set the data-theme attribute after successfully changing the theme
        $('body').data('theme', theme);

        // Notify the user about the theme change after AJAX success
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
