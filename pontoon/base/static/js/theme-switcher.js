document.addEventListener('DOMContentLoaded', function () {
  const themeHiddenInput = document.querySelector('[name="theme"]');
  const darkButton = document.querySelector('.dark');
  const lightButton = document.querySelector('.light');
  const systemButton = document.querySelector('.system');

  if (!themeHiddenInput || !darkButton || !lightButton || !systemButton) {
    console.error('Theme elements not found!');
    return;
  }

  darkButton.addEventListener('click', function () {
    applyTheme('Dark');
  });

  lightButton.addEventListener('click', function () {
    applyTheme('Light');
  });

  systemButton.addEventListener('click', function () {
    applyTheme('System');
  });
});

function applyTheme(theme) {
  const bodyElement = document.body;
  const themeHiddenInput = document.querySelector('[name="theme"]');

  // Remove all theme classes first
  bodyElement.classList.remove('dark-theme', 'light-theme');

  if (theme === 'Dark') {
    bodyElement.classList.add('dark-theme');
  } else if (theme === 'Light') {
    bodyElement.classList.add('light-theme');
  } else if (theme === 'System') {
    if (
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      bodyElement.classList.add('dark-theme');
    } else {
      bodyElement.classList.add('light-theme');
    }
  }

  // Update hidden input value
  themeHiddenInput.value = theme;
}

// document.addEventListener('DOMContentLoaded', function() {
//     const themeSelector = document.querySelector('[name="themes"]');

//     if (!themeSelector) {
//         console.error('Theme selector not found!');
//         return;
//     }

//     themeSelector.addEventListener('change', function() {
//         applyTheme(this.value);
//     });
// });

// function applyTheme(theme) {
//     alert("Hello")
//     const bodyElement = document.body;

//     if (theme === 'Dark') {
//         bodyElement.classList.add('dark-theme');
//         bodyElement.classList.remove('light-theme');
//     } else if (theme === 'Light') {
//         bodyElement.classList.add('light-theme');
//         bodyElement.classList.remove('dark-theme');
//     } else if (theme === 'System') {
//         if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
//             bodyElement.classList.add('dark-theme');
//             bodyElement.classList.remove('light-theme');
//         } else {
//             bodyElement.classList.add('light-theme');
//             bodyElement.classList.remove('dark-theme');
//         }
//     }
// }
