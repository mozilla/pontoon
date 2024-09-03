$(function () {
  // Toggle check box
  $('.check-box').click(function () {
    const self = $(this);

    const name = self.data('attribute');
    $(`[type=checkbox][name=${name}]`).click();

    self.toggleClass('enabled');

    // Toggle Transactional check box
    if (self.is('.email')) {
      $('.check-box.transactional').toggle(self.is('.enabled'));
    }
  });

  const container = $('#main .container');

  function isValidForm() {
    const $form = $('#send-message');
    $form.find('.errors').css('visibility', 'hidden');

    const isValidType =
      $form.find('.message-type .check-box').filter('.enabled').length > 0;

    const subject = $form.find('[name=subject]').val();
    const body = $form.find('[name=body]').val();

    const isValidRole =
      $form.find('.filter-user-role .check-box').filter('.enabled').length > 0;

    const isValidLocale = $form.find('[name=locales]').val();

    const isValidProject = $form.find('[name=projects]').val();

    if (!isValidType) {
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

    if (!isValidRole) {
      $form.find('.filter-user-role .errors').css('visibility', 'visible');
    }

    if (!isValidLocale) {
      $form.find('.filter-locale .errors').css('visibility', 'visible');
    }

    if (!isValidProject) {
      $form.find('.filter-project .errors').css('visibility', 'visible');
    }

    return (
      isValidType &&
      subject &&
      body &&
      isValidRole &&
      isValidLocale &&
      isValidProject
    );
  }

  // Send message
  container.on('click', '#send-message .send', function (e) {
    e.preventDefault();

    // Validate form
    if (!isValidForm()) {
      return;
    }

    const $form = $('#send-message');

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

  // By default, all locales and all projects are selected
  $('.multiple-team-selector')
    .find('.available .move-all')
    .click()
    .end()
    .find('.selected ul')
    .scrollTop(0);
  $('.multiple-project-selector')
    .find('.available .move-all')
    .click()
    .end()
    .find('.selected ul')
    .scrollTop(0);
});
