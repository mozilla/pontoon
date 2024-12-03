$(function () {
  const locale = $('#server').data('locale');

  // Update state from URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  let currentPage = parseInt(urlParams.get('pages')) || 1;
  let search = urlParams.get('search') || '';

  function updateURL() {
    const url = new URL(window.location);

    if (currentPage > 1) {
      url.searchParams.set('pages', currentPage);
    } else {
      url.searchParams.delete('pages');
    }

    if (search) {
      url.searchParams.set('search', search);
    } else {
      url.searchParams.delete('search');
    }

    history.replaceState(null, '', url);
  }

  function loadMoreEntries() {
    const tmList = $('#main .translation-memory-list');
    const loader = tmList.find('.skeleton-loader');

    // If the loader is already loading, don't load more entries
    if (loader.is('.loading')) {
      return;
    }

    loader.each(function () {
      $(this).addClass('loading');
    });

    $.ajax({
      url: `/${locale}/ajax/translation-memory/`,
      data: { page: currentPage + 1, search: search },
      success: function (data) {
        loader.each(function () {
          $(this).remove();
        });
        const tbody = tmList.find('tbody');
        if (currentPage === 0) {
          // Clear the table for a new search
          tbody.empty();
        }
        tbody.append(data);
        currentPage += 1;
        updateURL(); // Update the URL with the new pages count and search query
      },
      error: function () {
        Pontoon.endLoader('Error loading more TM entries.', 'error');
        loader.each(function () {
          $(this).removeClass('loading');
        });
      },
    });
  }

  $(window).scroll(function () {
    if (
      $(window).scrollTop() + $(window).height() >=
      $(document).height() - 300
    ) {
      // If there's no loader, there are no more entries to load
      if (!$('#main .translation-memory-list .skeleton-loader').length) {
        return;
      }
      loadMoreEntries();
    }
  });

  // Listen for search on Enter key press
  $('body').on('keypress', '.translation-memory .table-filter', function (e) {
    if (e.key === 'Enter') {
      currentPage = 0; // Reset page count for a new search
      search = $(this).val();
      loadMoreEntries();
    }
  });

  // Cancel action
  $('body').on('click', '.translation-memory .button.cancel', function () {
    const row = $(this).parents('tr');
    row.removeClass('deleting editing');
  });

  // Edit TM entries
  $('body').on('click', '.translation-memory .button.edit', function () {
    const row = $(this).parents('tr');
    row.addClass('editing');
    row.find('.target textarea').focus();
  });
  $('body').on('click', '.translation-memory .button.save', function () {
    const row = $(this).parents('tr');
    const ids = row.data('ids');
    const target = row.find('.target textarea').val();

    $.ajax({
      url: `/${locale}/ajax/translation-memory/edit/`,
      method: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        ids: ids,
        target: target,
      },
      success: function () {
        Pontoon.endLoader('TM entries edited.');

        let node = row.find('.target .content-wrapper');
        if (node.find('a').length) {
          node = node.find('a');
        }

        let new_target = target;
        if (target === '') {
          new_target = '<span class="empty">Empty string</span>';
        }

        node.html(new_target);
      },
      error: function () {
        Pontoon.endLoader('Error editing TM entries.', 'error');
      },
      complete: function () {
        row.removeClass('editing');
      },
    });
  });

  // Delete TM entries
  $('body').on('click', '.translation-memory .button.delete', function () {
    const row = $(this).parents('tr');
    row.addClass('deleting');
  });
  $('body').on(
    'click',
    '.translation-memory .button.are-you-sure',
    function () {
      const row = $(this).parents('tr');
      const ids = row.data('ids');

      $.ajax({
        url: `/${locale}/ajax/translation-memory/delete/`,
        method: 'POST',
        data: {
          csrfmiddlewaretoken: $('body').data('csrf'),
          ids: ids,
        },
        success: function () {
          row.addClass('fade-out');
          setTimeout(function () {
            row.remove();
            Pontoon.endLoader('TM entries deleted.');
          }, 500);
        },
        error: function () {
          Pontoon.endLoader('Error deleting TM entries.', 'error');
        },
        complete: function () {
          row.removeClass('deleting');
        },
      });
    },
  );

  const uploadWrapper = '.translation-memory .upload-wrapper';

  // Upload TM entries
  $('body').on('click', `${uploadWrapper} .upload`, function () {
    const controls = $(this).parents('.controls');
    controls.addClass('uploading');
  });
  // Cancel action
  $('body').on('click', `${uploadWrapper} .cancel`, function () {
    const controls = $(this).parents('.controls');
    controls.removeClass('uploading');
  });
  $('body').on('click', `${uploadWrapper} .confirm`, function () {
    const controls = $(this).parents('.controls');
    const fileInput = $('<input type="file" accept=".tmx">');
    fileInput.on('change', function () {
      controls.removeClass('uploading');

      const file = this.files[0];
      if (!file) {
        return;
      }

      const formData = new FormData();
      formData.append('tmx_file', file);
      formData.append('csrfmiddlewaretoken', $('body').data('csrf'));

      $.ajax({
        url: `/${locale}/ajax/translation-memory/upload/`,
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
          Pontoon.endLoader(response.message);
        },
        error: function (xhr) {
          Pontoon.endLoader(
            xhr.responseJSON?.message ?? 'Error uploading TMX file.',
            'error',
          );
        },
      });
    });

    fileInput.click();
  });
});
