$(function () {
  let currentPage = 1; // First page is loaded on page load
  let search = '';
  const locale = $('#server').data('locale');

  function loadMoreEntries() {
    const tmList = $('#main .container .translation-memory-list');
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
          // Clear the table if it's a new search
          tbody.empty();
        }
        tbody.append(data);
        currentPage += 1;
      },
      error: function () {
        Pontoon.endLoader('Error loading more TM entries.');
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
  $('body').on('keypress', '.table-filter', function (e) {
    if (e.key === 'Enter') {
      currentPage = 0; // Reset page count for a new search
      search = $(this).val();
      loadMoreEntries();
    }
  });

  // Cancel action
  $('body').on('click', '.button.cancel', function () {
    const row = $(this).parents('tr');
    row.removeClass('deleting editing');
  });

  // Edit TM entries
  $('body').on('click', '.button.edit', function () {
    const row = $(this).parents('tr');
    row.addClass('editing');
    row.find('.target textarea').focus();
  });
  $('body').on('click', '.button.save', function () {
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
        Pontoon.endLoader('Error editing TM entries.');
      },
      complete: function () {
        row.removeClass('editing');
      },
    });
  });

  // Delete TM entries
  $('body').on('click', '.button.delete', function () {
    const row = $(this).parents('tr');
    row.addClass('deleting');
  });
  $('body').on('click', '.button.are-you-sure', function () {
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
        Pontoon.endLoader('Error deleting TM entries.');
      },
      complete: function () {
        row.removeClass('deleting');
      },
    });
  });
});
