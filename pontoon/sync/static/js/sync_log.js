$(function () {
  // Remove any existing sync-status-* class
  function removeSyncStatusClasses($element) {
    $element.removeClass(function (index, className) {
      return (className.match(/(^|\s)sync-status-\S+/g) || []).join(' ');
    });
  }

  // Request to sync a project
  $('.sync').click(function (e) {
    e.preventDefault();

    const projectSlug = $(this).attr('project-slug');
    const $row = $(this).closest('tr');
    const $statusCell = $row.find('td').eq(1);

    removeSyncStatusClasses($statusCell);
    $statusCell.addClass('sync-status-other').text('Requested');

    $.ajax({
      url: `/admin/projects/${projectSlug}/sync/`,
      success: function () {
        // Reload the page in case of success to update the status correctly (it
        // could be a sync with no changes)
        location.reload();
      },
      error: function () {
        removeSyncStatusClasses($statusCell);
        $statusCell.addClass('sync-status-error').text('Error');
      },
    });
  });
});
