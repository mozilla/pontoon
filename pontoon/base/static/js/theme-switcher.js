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
      storeSystemTheme(newTheme);
    }
    $('body')
      .removeClass('dark-theme light-theme system-theme')
      .addClass(`${newTheme}-theme`);
  }

  /*
   * Storing system theme setting in a cookie makes the setting available to the server.
   * That allows us to set the theme class already in the Django template, which (unlike
   * setting it on the client) prevents FOUC.
   */
  function storeSystemTheme(systemTheme) {
    document.cookie = `system_theme=${systemTheme}; path=/; max-age=${
      60 * 60 * 24 * 365
    }; Secure`;
  }

  window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', function () {
      // Check the 'data-theme' attribute on the body element
      let userThemeSetting = $('body').data('theme');

      if (userThemeSetting === 'system') {
        applyTheme(userThemeSetting);
      }
    });

  if ($('body').data('theme') === 'system') {
    applyTheme('system');
  }

  $('.appearance .toggle-button button').click(function (e) {
    e.preventDefault();
    e.stopPropagation();

    var self = $(this);

    if (self.is('.active')) {
      return;
    }

    var theme = self.val();

    $.ajax({
      url:
        '/api/v1/user/' +
        $('#profile input[name="username"]').val() +
        '/theme/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        theme: theme,
      },
      success: function () {
        $('.appearance .toggle-button button').removeClass('active');
        $(`.appearance .toggle-button button[value=${theme}]`).addClass(
          'active',
        );
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
