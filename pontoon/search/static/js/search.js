$(function () {
  $('.search-input')
    .unbind('keydown.pontoon')
    .bind('keydown.pontoon', function (e) {
      if (e.which === 13) {
        $(this).trigger('enterKey');
        return false;
      }
    });

  const url = new URL(window.location.href);
  const params = url.searchParams;
  let currentPage = 1;
  let hasMore = false;
  let isLoading = false;

  function updateURL() {
    const pagesLoaded = currentPage - 1;
    if (pagesLoaded > 1) {
      url.searchParams.set('pages', pagesLoaded);
    } else {
      url.searchParams.delete('pages');
    }

    history.replaceState(null, '', url);
  }

  function loadMoreEntries() {
    return $.ajax({
      url: '/search/results/',
      type: 'GET',
      data: {
        page: currentPage,
        search: params.get('search'),
        locale: params.get('locale'),
        project: params.get('project'),
        search_identifiers: params.get('search_identifiers'),
        search_match_case: params.get('search_match_case'),
        search_match_whole_word: params.get('search_match_whole_word'),
      },
      success: function (response) {
        $('#entity-list').append(response.html);
        hasMore = response['has_more'];
        currentPage += 1;
        updateURL();
      },
      error: function () {
        Pontoon.endLoader('Oops, something went wrong.');
      },
      complete: function () {
        isLoading = false;
      },
    });
  }

  $(window).on('load', async function () {
    const pages = parseInt(params.get('pages')) || 1;

    if (params.get('search')) {
      Pontoon.NProgressUnbind();
      NProgress.start();
      for (let i = 1; i <= pages; i++) {
        await loadMoreEntries();
        NProgress.set(i / pages);
        if (!hasMore) {
          break;
        }
      }
      NProgress.done();
      Pontoon.NProgressBind();

      if ($('#entity-list').children().length <= 0) {
        $('#no-results').show();
      }
    }
  });

  $('.search-input').on('enterKey', function () {
    const $input = $('.search-input');
    const search = $input.val()?.trim();

    const url = new URL(window.location.href);
    url.search = '';

    const params = url.searchParams;
    params.set('search', search);

    const locale = $('.locale .selector .language').data().code;
    params.set('locale', locale);

    const project = $('.project .selector .selected-project').data().slug;

    if (project && project !== 'all-projects') {
      params.set('project', project);
    }

    const checkboxParamMap = {
      'search-identifiers-enabled': 'search_identifiers',
      'match-case-enabled': 'search_match_case',
      'match-whole-word-enabled': 'search_match_whole_word',
    };

    $('.check-box.enabled').each(function () {
      const attr = $(this).data('attribute');
      const param = checkboxParamMap[attr];
      if (param) {
        params.set(param, 'true');
      }
    });

    window.location.href = `${url.pathname}?${params.toString()}`;
  });

  $('.check-box').click(function () {
    const self = $(this);
    self.toggleClass('enabled');
  });

  $(window).on('scroll', function () {
    if (
      $(window).scrollTop() + $(window).height() >=
        $(document).height() - 2000 &&
      !isLoading &&
      hasMore
    ) {
      isLoading = true;
      loadMoreEntries();
    }
  });

  $(function () {
    const clipboard = new Clipboard('.copy');

    clipboard.on('success', function () {
      Pontoon.endLoader('Translation copied to clipboard.');
    });

    $(document).on('click', '.copy-btn', function (e) {
      e.preventDefault();
    });
  });
});
