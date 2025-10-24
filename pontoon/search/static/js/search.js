$(function () {
  $('.search-button').click(function () {
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
  let hasMore = $('.entity-list').data('has-more');
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
          response.entities.forEach(function (entity) {
            const entities_url = `/entities/${entity.id}/`;

            $('.entity-list').append(`
              <li class="entity-item">
                <span>${entity.string}</span>
                <span>${entity.key}</span>
                <span>Entity URL:</span>
                <a href="${entities_url}">${entities_url}</a>
                <div>
                  <span>${entity.project.slug}</span>
                  <span>${entity.project.name}</span>
                </div>

                <div>
                  <a>${entity.resource.path}</a>
                </div>

                <div>
                  <span>${entity.translation.locale.code}</span>
                  <span>${entity.translation.locale.name}</span>
                </div>

                <div>${entity.translation.string}</div>
              </li>
            `);
          });

          hasMore = response.has_more;
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
});
