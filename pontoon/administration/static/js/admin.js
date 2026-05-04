document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('toggle-projects');
  const toggleIcon = toggleBtn.querySelector('span');
  const enabledSection = document.querySelector('.enabled-projects');
  const disabledSection = document.querySelector('.disabled-projects');

  toggleBtn.addEventListener('click', () => {
    const showingDisabled = toggleBtn.dataset.showDisabled === 'true';

    enabledSection.style.display = showingDisabled ? 'block' : 'none';
    disabledSection.style.display = showingDisabled ? 'none' : 'block';

    toggleIcon.classList.toggle('fa-chevron-right', showingDisabled);
    toggleIcon.classList.toggle('fa-chevron-left', !showingDisabled);

    toggleBtn.classList.toggle('back');

    toggleBtn.dataset.showDisabled = (!showingDisabled).toString();
  });
});

$(function () {
  $('#recalculate-stats').on('click', function (e) {
    e.preventDefault();

    const button = $(this),
      title = button.html();

    if (button.is('.in-progress')) {
      return;
    }

    button.addClass('in-progress').html('Calculating...');

    $.ajax({
      url: '/admin/calculate-stats/',
      success() {
        button.html('Done');
      },
      error() {
        button.html('Whoops!');
      },
      complete() {
        setTimeout(function () {
          button.removeClass('in-progress').html(title);
        }, 2000);
      },
    });
  });
});
