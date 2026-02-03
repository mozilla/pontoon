$(function () {
  function updateURL() {
    const pagesLoaded = currentPage - 1;
    if (pagesLoaded > 1) {
      url.searchParams.set('pages', pagesLoaded);
    } else {
      url.searchParams.delete('pages');
    }

    history.replaceState(null, '', url);
  }

  function loadMoreEntries(options) {
    if (isLoading) {
      return;
    }

    isLoading = true;
    const pageCount = (options && options.pages) || 1;

    const data = {
      search: params.get('search'),
      locale: params.get('locale'),
      project: params.get('project'),
      search_identifiers: params.get('search_identifiers'),
      search_match_case: params.get('search_match_case'),
      search_match_whole_word: params.get('search_match_whole_word'),
    };

    if (options && options.pages) {
      data.pages = options.pages;
    } else {
      data.page = currentPage;
    }

    return $.ajax({
      url: '/search/results/',
      type: 'GET',
      data: data,
      success: function (response) {
        $('#entity-list').append(response.html);
        hasMore = response['has_more'];
        currentPage += pageCount;
        updateURL();
      },
      error: function () {
        Pontoon.endLoader('Oops, something went wrong.');
      },
      complete: function () {
        isLoading = false;
        if ($('#entity-list').children().length > 0) {
          $('#entity-list').show();
        } else {
          $('#entity-list').hide();
          $('#no-results').show();
        }
      },
    });
  }

  $('.search-input')
    .unbind('keydown.pontoon')
    .bind('keydown.pontoon', function (e) {
      if (e.which === 13) {
        $(this).trigger('enterKey');
        return false;
      }
    });

  $('.search-input').on('enterKey', function () {
    const search = $('.search-input').val()?.trim();
    if (!search) {
      return;
    }

    $('#no-results').hide();

    url.search = '';
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

    currentPage = 1;
    $('#entity-list').empty();
    loadMoreEntries();
  });

  $('.check-box').click(function () {
    const self = $(this);
    self.toggleClass('enabled');
  });

  $(window).on('scroll', function () {
    if (
      $(window).scrollTop() + $(window).height() >=
        $(document).height() - 2000 &&
      hasMore
    ) {
      loadMoreEntries();
    }
  });

  $(document).on('click', '.copy-btn', function (e) {
    e.preventDefault();
  });

  const url = new URL(window.location.href);
  const params = url.searchParams;
  const pages = parseInt(params.get('pages')) || 1;
  let currentPage = 1;
  let hasMore = false;
  let isLoading = false;

  if (params.get('search')) {
    loadMoreEntries({ pages: pages });
  }

  const clipboard = new Clipboard('.copy');

  clipboard.on('success', function () {
    Pontoon.endLoader('Translation copied to clipboard.');
  });
});
