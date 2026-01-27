$(function () {
  $('.search-btn').click(function () {
    $('.search-input').trigger('enterKey');
  });

  $('.search-input')
    .unbind('keydown.pontoon')
    .bind('keydown.pontoon', function (e) {
      if (e.which === 13) {
        $(this).trigger('enterKey');
        return false;
      }
    });

  $('.search-input').on('enterKey', function () {
    const searchOptions = {};

    searchOptions['search'] = $('.search-input').val();
    if (!searchOptions['search']) {
      return;
    }

    $('.check-box').each(function () {
      const self = $(this);
      if (self.hasClass('enabled')) {
        const attribute = self.data('attribute');
        searchOptions[attribute] = true;
      }
    });

    searchOptions['locale'] = $('.locale .selector .language').data().code;
    const selectedProject = $('.locale .selector .selected-project').data()
      .slug;

    if (selectedProject && selectedProject !== 'all-projects') {
      searchOptions['project'] = selectedProject;
    }

    const currentUrl = new URL(window.location.href);
    currentUrl.search = '';
    const params = currentUrl.searchParams;

    // search, project, locale selectors
    params.set('search', searchOptions['search']);
    if (searchOptions['project']) {
      params.set('project', searchOptions['project']);
    }
    params.set('locale', searchOptions['locale']);

    // checkboxes
    if (searchOptions['search-identifiers-enabled']) {
      params.set(
        'search_identifiers',
        searchOptions['search-identifiers-enabled'],
      );
    }
    if (searchOptions['match-case-enabled']) {
      params.set('search_match_case', searchOptions['match-case-enabled']);
    }
    if (searchOptions['match-whole-word-enabled']) {
      params.set(
        'search_match_whole_word',
        searchOptions['match-whole-word-enabled'],
      );
    }

    window.location.href = `${currentUrl.pathname}?${params.toString()}`;
  });

  $('.check-box').click(function () {
    const self = $(this);
    self.toggleClass('enabled');
  });

  let currentPage = 2;
  let hasMore = $('#entity-list').data('has-more');
  let isLoading = false;

  $(window).on('scroll', function () {
    if (
      $(window).scrollTop() + $(window).height() >=
        $(document).height() - 2000 &&
      !isLoading &&
      hasMore
    ) {
      isLoading = true;

      const currentUrl = new URL(window.location.href);
      const params = currentUrl.searchParams;

      $.ajax({
        url: '/ajax/more-translations/',
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
        },
        error: function () {
          Pontoon.endLoader('Oops, something went wrong.');
        },
        complete: function () {
          isLoading = false;
        },
      });
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
