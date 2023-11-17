// JavaScript to submit the import translations from csv form when a file is selected
document
  .getElementById('importCsvInput')
  .addEventListener('change', function (event) {
    if (event.target.files.length > 0) {
      // A file was selected, submit the form
      document.getElementById('importCsvForm').submit();
    }
  });
