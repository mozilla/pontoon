$('body').on('click', '#view-toggle', function (e) {
  e.stopPropagation();

  const table = $('.locale-list');
  table.toggleClass('show-score-view');

  const showScores = table.hasClass('show-score-view');

  // Keep each cells sort key in sync
  table.find('td.cell').each(function () {
    const td = $(this);
    const key = showScores
      ? td.attr('data-score-sort')
      : td.attr('data-base-sort');
    if (key !== undefined) {
      td.attr('data-sort', key);
    }
  });

  $('#view-toggle').text(showScores ? 'Show default' : 'Show scores');
});
