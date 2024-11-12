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
});
