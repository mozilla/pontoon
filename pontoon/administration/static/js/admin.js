document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('toggle-projects');
  const enabledSection = document.querySelector('.enabled-projects');
  const disabledSection = document.querySelector('.disabled-projects');

  const showingDisabled = toggleBtn.dataset.showDisabled === 'true';

  // Set initial text based on data attribute
  toggleBtn.textContent = showingDisabled
    ? toggleBtn.dataset.textShowEnabled
    : toggleBtn.dataset.textShowDisabled;

  toggleBtn.addEventListener('click', () => {
    const showingDisabled = toggleBtn.dataset.showDisabled === 'true';

    enabledSection.style.display = showingDisabled ? 'block' : 'none';
    disabledSection.style.display = showingDisabled ? 'none' : 'block';

    toggleBtn.textContent = showingDisabled
      ? toggleBtn.dataset.textShowDisabled
      : toggleBtn.dataset.textShowEnabled;

    toggleBtn.dataset.showDisabled = (!showingDisabled).toString();
  });
});
