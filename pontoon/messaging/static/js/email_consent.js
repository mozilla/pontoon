$(function () {
  // Toggle user profile attribute
  $('.buttons .button').click(function (e) {
    e.preventDefault();
    const self = $(this);

    $.ajax({
      url: '/dismiss-email-consent/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        value: self.is('.enable'),
      },
      success: function (data) {
        window.location.href = data.next;
      },
      error: function (request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      },
    });
  });
});
