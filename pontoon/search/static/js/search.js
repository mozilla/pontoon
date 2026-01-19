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
      const errorMessage = 'Search term cannot be empty.';
      $('.errors').html($('<p>').text(errorMessage));
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
  let errors = false;

  if ($('.errors').children().length > 0) {
    errors = true;
  }

  $(window).on('scroll', function () {
    if (
      $(window).scrollTop() + $(window).height() >=
        $(document).height() - 2000 &&
      !isLoading &&
      hasMore &&
      !errors
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
          const locale = params.get('locale');
          response['entities'].forEach(function (entity) {
            const $li = $(`
              <li class="entity-container">
                <div class="source-string-container">
                  <span class="source-string"></span>
                </div>
                <div class="translation-string-container">
                  <span class="translation-string"></span>
                </div>
                <div class="entity-info-container">
                  <div class="context">
                    <span class="title">CONTEXT</span>
                    <span class="entity-keys"></span>
                    <span class="divider entity-keys-divider">&bull;</span>
                    <a class="resource-path"></a>
                    <span class="divider">&bull;</span>
                    <a class="project"></a>
                  </div>
                </div>
                <div class="utility-btn-container controls clearfix">
                  <a class="all-locales-btn fas fa-globe" type="button" tabindex="-1"></a>
                  <a class="edit-btn fas fa-edit" type="button" tabindex="-1"></a>
                  <button class="button copy-btn far fa-copy" type="button" tabindex="-1"></button>
                </div>
              </li>
            `);

            $li.find('.source-string').text(entity['string']);
            $li
              .find('.translation-string')
              .text(entity['translation']['string']);
            $li.find('.resource-path').text(entity['resource']['path']);
            $li.find('.project').text(entity['project']['name']);

            $li
              .find('.resource-path')
              .attr(
                'href',
                `/${locale}/${entity['project']['slug']}/${entity['resource']['path']}`,
              );
            $li
              .find('.project')
              .attr('href', `/projects/${entity['project']['slug']}`);
            $li
              .find('.all-locales-btn')
              .attr('href', `/entities/${entity['id']}`);
            $li
              .find('.edit-btn')
              .attr(
                'href',
                `/${locale}/${entity['project']['slug']}/${entity['resource']['path']}/?string=${entity['id']}`,
              );
            $li
              .find('.copy-btn')
              .attr('data-clipboard-text', entity['translation']['string']);

            if (entity['resource']['format'] !== 'gettext') {
              $li.find('.entity-keys').text(entity['key'].join(', '));
            } else {
              $li.find('.entity-keys').remove();
              $li.find('.entity-keys-divider').remove();
            }

            $('#entity-list').append($li);
          });

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
      Pontoon.endLoader('Translation copied.');
    });

    $(document).on('click', '.copy-btn', function (e) {
      e.preventDefault();
    });
  });
});
