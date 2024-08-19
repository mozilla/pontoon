$(function () {
  let currentPage = 1;
  const locale = $('#server').data('locale');

  function loadMoreEntries() {
    const tm_list = $('#main .container .translation-memory-list');
    const loader = tm_list.find('.skeleton-loader');
    if (loader.is('.loading')) {
      return;
    }
    loader.each(function () {
      $(this).addClass('loading');
    });

    $.ajax({
      url: `/${locale}/ajax/translation-memory/`,
      data: { page: currentPage + 1 },
      success: function (data) {
        loader.each(function () {
          $(this).remove();
        });
        tm_list.find('tbody').append(data);
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
      loadMoreEntries();
    }
  });
});
