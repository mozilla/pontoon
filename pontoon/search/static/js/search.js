$(function () {
  const url = new URL(window.location.href);
  const pages = parseInt(url.searchParams.get('pages')) || 1;
  let currentPage = 1;
  let hasMore = false;
  let isLoading = false;

  function updateURL(mode) {
    const pagesLoaded = currentPage - 1;
    if (pagesLoaded > 1) {
      url.searchParams.set('pages', pagesLoaded);
    } else {
      url.searchParams.delete('pages');
    }

    if (mode === 'push') {
      history.pushState('', '', url);
    } else {
      history.replaceState('', '', url);
    }
  }

  function loadMoreEntries(options) {
    if (isLoading) {
      return;
    }

    isLoading = true;
    const pageCount = (options && options.pages) || 1;

    const data = {
      search: url.searchParams.get('search'),
      locale: url.searchParams.get('locale'),
      project: url.searchParams.get('project'),
      search_identifiers: url.searchParams.get('search_identifiers'),
      search_match_case: url.searchParams.get('search_match_case'),
      search_match_whole_word: url.searchParams.get('search_match_whole_word'),
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
        $('#entity-list-header').css('display', 'flex');
        hasMore = response['has_more'];
        currentPage += pageCount;

        if (options?.mode) {
          updateURL(options.mode);
        }
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
    url.searchParams.set('search', search);

    const locale = $('.locale .selector .language').data().code;
    url.searchParams.set('locale', locale);

    const project = $('.project .selector .selected-project').data().slug;

    if (project && project !== 'all-projects') {
      url.searchParams.set('project', project);
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
        url.searchParams.set(param, 'true');
      }
    });

    currentPage = 1;
    $('#entity-list').empty();
    loadMoreEntries({ mode: 'push' });
  });

  $('#search-menu .search.button').click(function () {
    $('.search-input').trigger('enterKey');
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
      loadMoreEntries({ mode: 'replace' });
    }
  });

  $(document).on('click', '.copy-btn', function (e) {
    e.preventDefault();
  });

  $(window).on('popstate', function () {
    url.href = window.location.href;
    const search = url.searchParams.get('search');
    currentPage = 1;
    hasMore = false;

    if (search) {
      $('#entity-list').empty();
      $('#no-results').hide();
      $('.search-input').val(search);
      const pages = parseInt(url.searchParams.get('pages')) || 1;
      loadMoreEntries({ pages });
    } else {
      $('#entity-list').empty().hide();
      $('#no-results').hide();
      $('.search-input').val('');
    }
  });

  if (url.searchParams.get('search')) {
    loadMoreEntries({ pages: pages });
  }

  const clipboard = new Clipboard('.copy');

  clipboard.on('success', function () {
    Pontoon.endLoader('Translation copied to clipboard.');
  });
});
