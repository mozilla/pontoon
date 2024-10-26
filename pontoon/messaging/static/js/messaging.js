$(function () {
  const container = $('#main .container');
  const converter = new showdown.Converter({
    simpleLineBreaks: true,
  });
  const nf = new Intl.NumberFormat('en');
  let inProgress = false;

  function validateForm() {
    const $form = $('#send-message');

    const isValidType =
      $form.find('.message-type [type=checkbox]:checked').length > 0;

    const isValidSubject = $form.find('[name=subject]').val();
    const isValidBody = $form.find('#body').val();

    const isValidRole =
      $form.find('.user-roles [type=checkbox]:checked').length > 0;

    const isValidLocale = $form.find('[name=locales]').val();

    const isValidProject = $form.find('[name=projects]').val().length;

    const isValidTranslationMinimum = $form
      .find('[name=translation_minimum]')[0]
      .checkValidity();
    const isValidTranslationMaximum = $form
      .find('[name=translation_maximum]')[0]
      .checkValidity();
    const isValidReviewMinimum = $form
      .find('[name=review_minimum]')[0]
      .checkValidity();
    const isValidReviewMaximum = $form
      .find('[name=review_maximum]')[0]
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
    function updateMultipleItemSelector(source, target, item) {
      const allProjects = !$(`${source}.available li:not(.no-match)`).length;
      const projectsSelected = $(`${source}.selected li:not(.no-match)`)
        .map(function () {
          return $(this).find(item).text();
        })
        .get();
      const projectsDisplay = allProjects ? 'All' : projectsSelected.join(', ');
      $(`#review ${target} .value`).html(projectsDisplay);
    }

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

    // Fetch recipients
    $('#review .controls .fetching').show();
    $('#review .controls .error').hide();
    $('#review .controls .send.active').hide().find('.value').html('');

    $.ajax({
      url: '/messaging/ajax/fetch-recipients/',
      type: 'POST',
      data: $('#send-message').serialize(),
      success: function (data) {
        const count = nf.format(data.recipients.length);
        $('#review .controls .send.active').show().find('.value').html(count);
        $('#compose [name=recipient_ids]').val(data.recipients);
      },
      error: function () {
        $('#review .controls .error').show();
      },
      complete: function () {
        $('#review .controls .fetching').hide();
      },
    });

    // Subject
    $('#review .subject .value').html($('#id_subject').val());

    // Body
    const bodyValue = $('#body').val();
    const html = converter.makeHtml(bodyValue);
    $('#review .body .value').html(html);

    // Update hidden textarea with the HTML content to be sent to backend
    $('#compose [name=body]').val(html);

    // User roles
    const userRoles = $('#compose .user-roles .enabled')
      .map(function () {
        return $(this).find('.label').text();
      })
      .get();
    $('#review .user-roles .value').html(userRoles.join(', '));

    // Locales
    updateMultipleItemSelector('.locale', '.locales', '.code');

    // Projects
    updateMultipleItemSelector('.project .item', '.projects', '.item');

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

  function loadPanelContent(path) {
    if (inProgress) {
      inProgress.abort();
    }

    const panel = container.find('.right-column');
    const relative_path = path.split('/messaging/')[1];
    const isSentPage = relative_path === 'sent/';
    const menu_path = isSentPage ? '/messaging/sent/' : '/messaging/';

    // Update menu selected state
    container
      .find(`.left-column a[href="${menu_path}"]`)
      .parents('li')
      .addClass('selected')
      .siblings()
      .removeClass('selected');

    panel.empty();

    inProgress = $.ajax({
      url: `/messaging/ajax/${relative_path}`,
      success: function (data) {
        panel.append(data);

        if (isSentPage) {
          // Dissolve new message state
          setTimeout(function () {
            container.find('.message.new').removeClass('new');
          }, 1000);
        } else if (relative_path) {
          // Convert body content from HTML to markdown
          const html = $('#compose [name=body]').val();
          const markdown = converter.makeMarkdown(html);
          $('#body').val(markdown);
        }
      },
      error: function (error) {
        if (error.status === 0 && error.statusText !== 'abort') {
          const message = $('<p>', {
            class: 'no-results',
            html: 'Oops, something went wrong.',
          });

          panel.append(message);
        }
      },
    });
  }

  // Load panel content on page load
  loadPanelContent(window.location.pathname);

  // Load panel content on history change
  window.onpopstate = function () {
    loadPanelContent(window.location.pathname);
  };

  // Load panel content on menu click
  container.on(
    'click',
    '.left-column a, .right-column .use-as-template',
    function (e) {
      // Keep default middle-, shift-, control- and command-click behaviour
      if (e.which === 2 || e.metaKey || e.shiftKey || e.ctrlKey) {
        return;
      }

      e.preventDefault();

      const path = $(this).attr('href');
      loadPanelContent(path);
      window.history.pushState({}, '', path);
    },
  );

  // Toggle check box
  container.on('click', '.check-box', function () {
    const self = $(this);
    const checkbox = self.find('[type=checkbox]')[0];

    checkbox.checked = !checkbox.checked;
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

    const $form = $('#send-message');
    const sendToMyself = $(this).is('.to-myself');

    // Distinguish between Send and Send to myself
    $('#id_send_to_myself').prop('checked', sendToMyself);

    // Submit form
    $.ajax({
      url: $form.prop('action'),
      type: $form.prop('method'),
      data: $form.serialize(),
      success: function () {
        Pontoon.endLoader('Message sent.');
        if (!sendToMyself) {
          container.find('.left-column .sent a').click();
        }
      },
      error: function () {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      },
    });
  });
});
