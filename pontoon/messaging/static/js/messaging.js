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

  function validateForm() {
    const $form = $('#send-message');

    const isValidType =
      $form.find('.message-type .check-box').filter('.enabled').length > 0;

    const isValidSubject = $form.find('[name=subject]').val();
    const isValidBody = $form.find('[name=body]').val();

    const isValidRole =
      $form.find('.filter-user-role .check-box').filter('.enabled').length > 0;

    const isValidLocale = $form.find('[name=locales]').val();

    const isValidProject = $form.find('[name=projects]').val();

    const isValidTranslationMinimum = $form.find('#translation-minimum')[0].checkValidity();
    const isValidTranslationMaximum = $form.find('#translation-maximum')[0].checkValidity();
    const isValidReviewMinimum = $form.find('#review-minimum')[0].checkValidity();
    const isValidReviewMaximum = $form.find('#review-maximum')[0].checkValidity();

    $form.find('.errors').css('visibility', 'hidden');

    function showErrorIfNotValid(isValid, selector) {
      if (!isValid) {
        $form.find(selector).find('.errors').css('visibility', 'visible');
      }
    }

    showErrorIfNotValid(isValidType, '.message-type');
    showErrorIfNotValid(isValidSubject, '.subject');
    showErrorIfNotValid(isValidBody, '.body');
    showErrorIfNotValid(isValidRole, '.filter-user-role');
    showErrorIfNotValid(isValidLocale, '.filter-locale');
    showErrorIfNotValid(isValidProject, '.filter-project');
    showErrorIfNotValid(isValidTranslationMinimum, '.filter-translation > .minimum');
    showErrorIfNotValid(isValidTranslationMaximum, '.filter-translation > .maximum');
    showErrorIfNotValid(isValidReviewMinimum, '.filter-review > .minimum');
    showErrorIfNotValid(isValidReviewMaximum, '.filter-review > .maximum');

    return (
      isValidType &&
      isValidSubject &&
      isValidBody &&
      isValidRole &&
      isValidLocale &&
      isValidProject &&
      isValidTranslationMinimum &&
      isValidTranslationMaximum &&
      isValidReviewMinimum &&
      isValidReviewMaximum
    );
  }

  // Send message
  container.on('click', '#send-message .send', function (e) {
    e.preventDefault();

    const $form = $('#send-message');

    // Validate form
    const isValidForm = validateForm();
    if (!isValidForm) {
      // Scroll to the first visible error
      const visibleErrors = $form.find('.errors').filter(function () {
        return $(this).css('visibility') === 'visible';
      });
      if (visibleErrors.length) {
        $([document.documentElement, document.body]).animate(
          {
            scrollTop: visibleErrors.first().parent().offset().top,
          },
          400,
        );
      }
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

  // By default, all locales and all projects are selected
  $('.multiple-team-selector')
    .find('.available .move-all')
    .click()
    .end()
    .find('.selected ul')
    .scrollTop(0);
  $('.multiple-item-selector')
    .find('.available .move-all')
    .click()
    .end()
    .find('.selected ul')
    .scrollTop(0);
});
