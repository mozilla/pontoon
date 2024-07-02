$(function () {
  // Toggle check box
  $('.check-box').click(function () {
    const self = $(this);

    const name = self.data('attribute');
    $(`[type=checkbox][name=${name}]`).click();

    self.toggleClass('enabled');
  });

  const container = $('#main .container');

  function isValidForm($form, isNotification, isEmail, subject, body) {
    $form.find('.errors').css('visibility', 'hidden');

    if (!isNotification && !isEmail) {
      $form.find('.message-type .errors').css('visibility', 'visible');
    }

    if (!subject) {
      $form
        .find('.message-editor .subject .errors')
        .css('visibility', 'visible');
    }

    if (!body) {
      $form.find('.message-editor .body .errors').css('visibility', 'visible');
    }

    return (isNotification || isEmail) && subject && body;
  }

  // Send message
  container.on('click', '#send-message .send', function (e) {
    e.preventDefault();
    const $form = $('#send-message');

    const isNotification = $('.message-type .check-box.notification').is(
      '.enabled',
    );
    const isEmail = $('.message-type .check-box.email').is('.enabled');
    const subject = $form.find('[name=subject]').val();
    const body = $form.find('[name=body]').val();

    // Validate form
    if (!isValidForm($form, isNotification, isEmail, subject, body)) {
      return;
    }

    // Submit form
    $.ajax({
      url: $form.prop('action'),
      type: $form.prop('method'),
      data: $form.serialize(),
      success: function () {
        Pontoon.endLoader('Message sent.');
      },
      error: function () {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      },
    });
  });
});
