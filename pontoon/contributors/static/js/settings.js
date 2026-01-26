$(function () {
  $('.field .input')
    .unbind('keydown.pontoon')
    .bind('keydown.pontoon', function (e) {
      if (e.which === 13) {
        $(this).trigger('blur');
        return false;
      }
    });

  $('.field .input').on('blur', function (e) {
    e.preventDefault();

    const self = $(this);
    const value = self.val().trim();
    const attribute = this.dataset.attribute;
    const originalValue = this.dataset.originalValue || '';

    if (value === originalValue) {
      self.parents('.field').find('.errorlist').empty();

      if (attribute === 'contact_email') {
        if (value !== '') {
          self.parents('.field').find('.help').addClass('hide');
          self.parents('.field').find('.verify').removeClass('hide');
        } else {
          self.parents('.field').find('.help').removeClass('hide');
          self.parents('.field').find('.verify').addClass('hide');
        }
      }
      return;
    }

    this.dataset.originalValue = value;
    $.ajax({
      url: '/user/attributes/field/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        [attribute]: value,
      },
      success() {
        // contact_email special case
        if (attribute === 'contact_email') {
          if (value !== '') {
            self.parents('.field').find('.help').addClass('hide');
            self.parents('.field').find('.verify').removeClass('hide');
          } else {
            self.parents('.field').find('.help').removeClass('hide');
            self.parents('.field').find('.verify').addClass('hide');
          }
        }

        self.parents('.field').find('.errorlist').empty();
        const message = 'Settings saved.';
        Pontoon.endLoader(message);
      },
      error: (response) => {
        this.dataset.originalValue = originalValue;
        // contact_email special case
        if (attribute === 'contact_email') {
          self.parents('.field').find('.help').addClass('hide');
          self.parents('.field').find('.verify').addClass('hide');
        }

        const errorContainer = self.parents('.field').find('.errorlist');
        errorContainer.empty();
        for (const error of Object.values(response.responseJSON.errors)) {
          errorContainer.append($('<p>').text(error.join(', ')));
        }
      },
    });
  });

  function saveLocalesOrder() {
    const selectedLocales = $('.multiple-team-selector .locale.selected')
      .find('input[type=hidden]')
      .val();

    $.ajax({
      url: '/user/attributes/selector/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        locales_order: selectedLocales,
      },
      success() {
        const message = 'Settings saved.';
        Pontoon.endLoader(message);
      },
      error(request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      },
    });
  }

  $('body').on(
    'click',
    '.multiple-team-selector .locale.select li',
    saveLocalesOrder,
  );

  $('body').on('click', '.multiple-team-selector .move-all', saveLocalesOrder);

  // Handle toggle buttons
  $('.toggle-button button').click(function (e) {
    e.preventDefault();

    const self = $(this);

    // Theme toggle is handled separately
    if (self.parents('.appearance').length) {
      return;
    }

    if (self.is('.active')) {
      return;
    }

    const attribute = self.data('attribute');
    const value = self.val();

    $.ajax({
      url: '/user/attributes/toggle/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        attribute: attribute,
        value: value,
      },
      success() {
        self.addClass('active');
        self.siblings().removeClass('active');

        const label = self.parents('.field').find('.toggle-label').text();

        let message = `${label} set to ${value}.`;
        if (self.parents('section.data-visibility').length) {
          message = `${label} visibility set to ${value}.`;
        }
        Pontoon.endLoader(message);
      },
      error(request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      },
    });
  });

  $('.generate-token-btn').click(function (e) {
    e.preventDefault();

    const csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
      url: '/generate-token/',
      type: 'POST',
      data: {
        name: $('.token-name-input').val(),
        csrfmiddlewaretoken: csrfmiddlewaretoken,
      },
      success(response) {
        if (response.status !== 'success') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
          return;
        }

        const newTokenHTML = `
        <li class="token-card created controls clearfix" data-token-id="${response.data['new_token_id']}">
            <div class="token-header">
              <span class="token-name">${response.data['new_token_name']}</span>
              <div class="right">
                <div class="status active">
                  <span class="icon fas fa-check-circle"></span>
                  <span class="title">Status:</span>
                  <span class="value">Active</span>
                </div>
                <button type="button" class="button delete-btn far fa-trash-alt" tabindex="-1" data-token-id="${response.data['new_token_id']}"></button>
              </div>
            </div>
            <div class="token-info-container">
              <div class="token-info">
                <span class="icon fas fa-calendar-alt"></span>
                <span>Expires on:</span> 
                <span class="date">${response.data['new_token_expires_at']}</span>
              </div>
            </div>
            <div class="token-details">
              <input class="token-value" type="text" value="${response.data['new_token_secret']}" readonly></input>
              <button type="button" class="button copy-btn far fa-copy" tabindex="-1" data-clipboard-text="${response.data['new_token_secret']}" ></button>
            </div>
            <p class="copy-message">Make sure to copy your personal access token now as you will not be able to see it again.</p>
        </li>
        `;

        $('#pat-settings').find('.error-message').empty();
        $('.token-name-input').val('');
        $('.generate-token-btn').prop('disabled', true);
        $('.pat-list').append(newTokenHTML);
        Pontoon.endLoader('Token created.');
      },
      error(response) {
        const errorContainer = $('#pat-settings').find('.error-message');
        errorContainer.empty();

        for (const error of Object.values(response.responseJSON.errors)) {
          const errorMessages = error.join(', ');
          errorContainer.append($('<p>').text(errorMessages));
        }
      },
    });
  });

  $(document).on('click', '.delete-btn', function (e) {
    e.preventDefault();

    const tokenId = $(this).data('token-id');
    const csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
      url: `/delete-token/${tokenId}/`,
      type: 'POST',
      data: {
        csrfmiddlewaretoken: csrfmiddlewaretoken,
      },
      success(response) {
        if (response.status === 'success') {
          $(`li[data-token-id="${tokenId}"]`).remove();
        }
      },
      error() {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      },
    });
  });

  const clipboard = new Clipboard('.copy-btn');

  clipboard.on('success', function () {
    $('.clipboard-success').remove();
    Pontoon.endLoader('Token copied.');
  });

  $(document).on('click', '.copy-btn', function (e) {
    e.preventDefault();
  });

  $('.token-name-input').on('input', function () {
    $('.generate-token-btn').prop('disabled', $(this).val().trim() === '');
  });

  // Handle checkboxes
  $('.check-box').click(function () {
    const self = $(this);

    $.ajax({
      url: '/user/attributes/toggle/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        attribute: self.data('attribute'),
        value: !self.is('.enabled'),
      },
      success() {
        self.toggleClass('enabled');

        // If notification type disabled, uncheck email checkbox
        if (self.parents('.notifications').length && !self.is('.enabled')) {
          const emailChecbox = self.next('.check-box');
          if (emailChecbox.length) {
            emailChecbox.removeClass('enabled');
          }
        }

        Pontoon.endLoader('Settings saved.');
      },
      error(request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      },
    });
  });

  // Save custom homepage
  $('#homepage .locale .menu li:not(".no-match")').click(function () {
    const custom_homepage = $(this).find('.language').data('code');

    $.ajax({
      url: '/save-custom-homepage/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        custom_homepage: custom_homepage,
      },
      success(data) {
        if (data === 'ok') {
          Pontoon.endLoader('Custom homepage saved.');
        }
      },
      error(request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      },
    });
  });

  // Save preferred source locale
  $('#preferred-locale .locale .menu li:not(".no-match")').click(function () {
    const preferred_source_locale = $(this).find('.language').data('code');

    $.ajax({
      url: '/save-preferred-source-locale/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        preferred_source_locale: preferred_source_locale,
      },
      success(data) {
        if (data === 'ok') {
          Pontoon.endLoader('Preferred source locale saved.');
        }
      },
      error(request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      },
    });
  });

  const deleteUserModal = $('#delete-user-modal')[0];

  $(document).on('click', '.delete-user-btn', function (e) {
    e.preventDefault();

    deleteUserModal.showModal();
  });

  $(document).on('click', '#delete-user-confirm', function (e) {
    e.preventDefault();

    deleteUserModal.close();

    const csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
      url: `/user/delete/`,
      type: 'POST',
      data: {
        csrfmiddlewaretoken: csrfmiddlewaretoken,
      },
      success() {
        window.location.href = '/';
      },
      error() {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      },
    });
  });

  $(document).on('click', '#delete-user-cancel', function (e) {
    e.preventDefault();

    deleteUserModal.close();
  });

  $(deleteUserModal).on('click', function (e) {
    if (e.target === deleteUserModal) {
      deleteUserModal.close();
    }
  });
});
