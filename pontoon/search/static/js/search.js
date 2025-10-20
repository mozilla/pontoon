$(function () {
  $('.search-button').click(function () {
    const searchOptions = {};

    searchOptions['search'] = $('.search-input').val();
    if (!searchOptions['search']) {
      const errorMessage = 'Search term cannot be empty.';
      $('.errors').html($('<p>').text(errorMessage));
      return;
    } else if (searchOptions['search'].length < 2) {
      const errorMessage = 'Search term should be at least 2 characters long.';
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
});
