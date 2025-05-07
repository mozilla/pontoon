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
