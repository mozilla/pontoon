$(function () {
  const clipboard = new Clipboard('.copy-btn');

  clipboard.on('success', function () {
    $('.clipboard-success').remove();
    Pontoon.endLoader('Translation copied.');
  });

  $(document).on('click', '.copy-btn', function (e) {
    e.preventDefault();
  });
});
