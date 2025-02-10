$(function () {
  // Request to sync a project
  $('.sync').click(function (e) {
    e.preventDefault();

    const projectSlug = $(this).attr('project-slug');
    Pontoon.endLoader('Sync in progress...');
    $.ajax({
      url: `/admin/projects/${projectSlug}/sync/`,
      success: function () {
        // Reload the page in case of success to update the status correctly (it
        // could be a sync with no changes)
        location.reload();
      },
      error: function () {
        Pontoon.endLoader('Unable to sync the project.', 'error');
      },
    });
  });
});
