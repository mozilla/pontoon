$(function () {
  const container = $('#main .container');
  const converter = new showdown.Converter({
    simpleLineBreaks: true,
  });

  function validateForm() {
    const $form = $('#send-message');

    const isValidType =
      $form.find('.message-type .check-box').filter('.enabled').length > 0;

    const isValidSubject = $form.find('[name=subject]').val();
    const isValidBody = $form.find('[name=body]').val();

    const isValidRole =
      $form.find('.user-roles .check-box').filter('.enabled').length > 0;

    const isValidLocale = $form.find('[name=locales]').val();

    const isValidProject = $form.find('[name=projects]').val();

    const isValidTranslationMinimum = $form
      .find('#translation-minimum')[0]
      .checkValidity();
    const isValidTranslationMaximum = $form
      .find('#translation-maximum')[0]
      .checkValidity();
    const isValidReviewMinimum = $form
      .find('#review-minimum')[0]
      .checkValidity();
    const isValidReviewMaximum = $form
      .find('#review-maximum')[0]
      .checkValidity();

    $form.find('.errors').css('visibility', 'hidden');

    function showErrorIfNotValid(isValid, selector) {
      if (!isValid) {
        $form.find(selector).find('.errors').css('visibility', 'visible');
      }
    }

    showErrorIfNotValid(isValidType, '.message-type');
    showErrorIfNotValid(isValidSubject, '.subject');
    showErrorIfNotValid(isValidBody, '.body');
    showErrorIfNotValid(isValidRole, '.user-roles');
    showErrorIfNotValid(isValidLocale, '.locale');
    showErrorIfNotValid(isValidProject, '.project');
    showErrorIfNotValid(
      isValidTranslationMinimum,
      '.submitted-translations .minimum',
    );
    showErrorIfNotValid(
      isValidTranslationMaximum,
      '.submitted-translations .maximum',
    );
    showErrorIfNotValid(isValidReviewMinimum, '.preformed-reviews .minimum');
    showErrorIfNotValid(isValidReviewMaximum, '.preformed-reviews .maximum');

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

  function updateReviewPanel() {
    function updateFields(filter) {
      let show = false;
      $(`#compose .${filter} > div`).each(function () {
        const className = $(this).attr('class');
        const values = [];

        $(this)
          .find('.field')
          .each(function () {
            const label = $(this).find('label').text();
            let value = $(this).find('input').val().trim();
            if (value) {
              if (className === 'date') {
                value = new Date(value).toLocaleDateString();
              }
              values.push(`${label}: ${value}`);
              show = true;
            }
          });

        $(`#review .${filter} .${className}`).html(values.join(', '));
      });
      $(`#review .${filter}`).toggle(show);
    }

    // Subject
    $('#review .subject p').html($('#subject').val());

    // Body
    const bodyValue = $('#body').val();
    const html = converter.makeHtml(bodyValue);
    $('#review .body .value').html(html);

    // User roles
    const userRoles = $('#compose .user-roles .enabled')
      .map(function () {
        return $(this).find('.label').text();
      })
      .get();
    $('#review .user-roles .value').html(userRoles.join(', '));

    // Locales
    const allLocalesSelected = !$('.locale.available li:not(.no-match)').length;
    const localesSelected = $('.locale.selected li:not(.no-match)')
      .map(function () {
        return $(this).find('.code').text();
      })
      .get();
    const localesDisplay = allLocalesSelected ? 'All' : localesSelected.length;
    const localesTitle = localesSelected.join(', ');
    $('#review .locales .value')
      .html(localesDisplay)
      .attr('title', localesTitle);

    // Projects
    const allProjectsSelected = !$('.project .item.available li:not(.no-match)')
      .length;
    const projectsSelected = $('.project .item.selected li:not(.no-match)')
      .map(function () {
        return $(this).find('.item').text();
      })
      .get();
    const projectsDisplay = allProjectsSelected
      ? 'All'
      : projectsSelected.length;
    const projectsTitle = projectsSelected.join(', ');
    $('#review .projects .value')
      .html(projectsDisplay)
      .attr('title', projectsTitle);

    // Submitted translations
    updateFields('submitted-translations');

    // Performed reviews
    updateFields('performed-reviews');

    // Last login
    updateFields('last-login');

    // Message types
    let messageTypes = $('.message-type .enabled')
      .map(function () {
        return $(this).find('.label').text();
      })
      .get();
    const isTransactional = messageTypes.includes('Transactional');
    if (isTransactional) {
      messageTypes.push('Transactional Email');
      messageTypes = messageTypes.filter(
        (item) => item !== 'Email' && item !== 'Transactional',
      );
    }
    $('#review .message-type .value').html(
      `The message will be sent as ${messageTypes.join(' and ')}.`,
    );
    $('#review .message-type .transactional').toggle(isTransactional);
  }

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

  // Toggle check box
  $('.check-box').click(function () {
    const self = $(this);

    const name = self.data('attribute');
    $(`[type=checkbox][name=${name}]`).click();

    self.toggleClass('enabled');

    // Toggle Transactional check box
    if (self.is('.email')) {
      $('.check-box.transactional').toggle(self.is('.enabled'));

      // Disable Transactional check box if Email gets disabled
      if (!self.is('.enabled')) {
        $('.check-box.transactional.enabled').click();
      }
    }
  });

  // Toggle between Edit and Review mode
  container.on('click', '.controls .toggle.button', function (e) {
    e.preventDefault();

    // Validate form
    if ($(this).is('.review')) {
      const isValidForm = validateForm();

      if (!isValidForm) {
        // Scroll to the first visible error
        const visibleErrors = $('#send-message .errors').filter(function () {
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

      updateReviewPanel();
    }

    $($(this).data('target')).show().siblings().hide();

    // Scroll to the top
    window.scrollTo(0, 0);
  });

  // Send message
  container.on('click', '.controls .send.button', function (e) {
    e.preventDefault();

    // Distinguish between Send and Send to myself
    $('.send-to-myself').prop('checked', $(this).is('.to-myself'));

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
});
