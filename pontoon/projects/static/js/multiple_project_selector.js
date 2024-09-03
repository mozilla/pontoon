// Contains behaviours of widgets that are shared between admin and end-user interface.
$(function () {
  /**
   * Function keeps track of inputs that contain information about the order of selected projects.
   */
  function updateSelectedProjects() {
    const $selectedList = $('.multiple-project-selector .project.selected'),
      $selectedProjectsField = $selectedList.find('input[type=hidden]'),
      selectedProjects = $selectedList
        .find('li[data-id]')
        .map(function () {
          return $(this).data('id');
        })
        .get();

    $selectedProjectsField.val(selectedProjects.join());
  }

  // Choose projects
  $('body').on(
    'click',
    '.multiple-project-selector .project.select li',
    function () {
      const ls = $(this).parents('.project.select'),
        target = ls.siblings('.project.select').find('ul'),
        item = $(this).remove();

      target.append(item);
      target.scrollTop(target[0].scrollHeight);
      updateSelectedProjects();
    },
  );

  // Choose/remove all projects
  $('body').on('click', '.multiple-project-selector .move-all', function (e) {
    e.preventDefault();
    const ls = $(this).parents('.project.select'),
      target = ls.siblings('.project.select').find('ul'),
      items = ls.find('li:visible:not(".no-match")').remove();

    target.append(items);
    target.scrollTop(target[0].scrollHeight);
    updateSelectedProjects();
  });

  if ($.ui && $.ui.sortable) {
    $('.multiple-project-selector .project.select .sortable').sortable({
      axis: 'y',
      containment: 'parent',
      update: updateSelectedProjects,
      tolerance: 'pointer',
    });
  }

  $('body').on('submit', 'form.user-projects-settings', updateSelectedProjects);
});
