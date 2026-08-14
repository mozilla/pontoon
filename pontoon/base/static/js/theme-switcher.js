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

    // Let theme-dependent UI (e.g. contribution chart) update
    document.dispatchEvent(
      new CustomEvent('themechange', { detail: { theme: newTheme } }),
    );
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
      const userThemeSetting = $('body').data('theme');

      if (userThemeSetting === 'system') {
        applyTheme(userThemeSetting);
      }
    });

  if ($('body').data('theme') === 'system') {
    applyTheme('system');
  }

  $('.appearance .toggle-button button').click(function (e) {
    const self = $(this);

    if (self.closest('.editor-theme-field').length) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    if (self.is('.active')) {
      return;
    }

    const theme = self.val();
    const mainSelector = self
      .closest('.appearance')
      .find('.toggle-button button')
      .not('.editor-theme-field .toggle-button button');

    $.ajax({
      url: '/user/theme/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        theme: theme,
      },
      success: function () {
        mainSelector.removeClass('active');
        mainSelector.filter(`[value=${theme}]`).addClass('active');
        applyTheme(theme);

        // Set the data-theme attribute after successfully changing the theme
        $('body').data('theme', theme);
      },
      error: function () {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      },
    });
  });

  $('.appearance .editor-theme-field .toggle-button button').click(
    function (e) {
      e.preventDefault();
      e.stopPropagation();

      const self = $(this);

      if (self.is('.active')) {
        return;
      }

      const editorTheme = self.val();
      const editorSelector =
        '.appearance .editor-theme-field .toggle-button button';

      $.ajax({
        url: '/user/editor-theme/',
        type: 'POST',
        data: {
          csrfmiddlewaretoken: $('body').data('csrf'),
          editor_theme: editorTheme,
        },
        success: function () {
          $(editorSelector).removeClass('active');
          $(`${editorSelector}[value=${editorTheme}]`).addClass('active');
          $('body').attr('data-editor-theme', editorTheme);
        },
        error: function () {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        },
      });
    },
  );
});
