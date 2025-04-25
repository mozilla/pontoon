document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('toggle-projects');
  const enabledSection = document.querySelector('.enabled-projects');
  const disabledSection = document.querySelector('.disabled-projects');

  const showingDisabled = toggleBtn.dataset.showDisabled === 'true';
  const iconLeft = '<span class="fa fa-chevron-left"></span>';
  const iconRight = '<span class="fa fa-chevron-right"></span>';

  // Set initial text based on data attribute
  toggleBtn.innerHTML = showingDisabled
    ? iconLeft + toggleBtn.dataset.textShowEnabled
    : toggleBtn.dataset.textShowDisabled + iconRight;

  toggleBtn.addEventListener('click', () => {
    const showingDisabled = toggleBtn.dataset.showDisabled === 'true';

    enabledSection.style.display = showingDisabled ? 'block' : 'none';
    disabledSection.style.display = showingDisabled ? 'none' : 'block';

    toggleBtn.innerHTML = showingDisabled
      ? toggleBtn.dataset.textShowDisabled + iconRight
      : iconLeft + toggleBtn.dataset.textShowEnabled;

    toggleBtn.dataset.showDisabled = (!showingDisabled).toString();
  });
});
