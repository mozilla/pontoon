$(function () {
  $('#account-status-form').on('submit', function (event) {
    event.preventDefault();

    const form = $(this);
    $.ajax({
      url: form.attr('action'),
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
      },
      success: function () {
        location.reload();
      },
    });
  });
});
