$(function () {
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
      url: '/api/v1/user/' + $('#profile input[name="username"]').val() + '/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        attribute: attribute,
        value: value,
      },
      success: function () {
        self.addClass('active');
        self.siblings().removeClass('active');

        const label = self.parents('.field').find('.toggle-label').text();

        let message = `${label} set to ${value}.`;
        if (self.parents('section.data-visibility').length) {
          message = `${label} visibility set to ${value}.`;
        }
        Pontoon.endLoader(message);
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
      success: function (response) {
        if (response.status !== 'success') {
          return;
        }

        const li = $('<li>').attr(
          'data-token-id',
          response.data['new_token_id'],
        );

        const tokenCard = $('<div>').addClass(
          'token-card created controls clearfix',
        );
        const tokenHeader = $('<div>').addClass('token-header');

        tokenHeader.append(
          $('<span>')
            .addClass('token-name')
            .text(response.data['new_token_name']),
        );

        const headerControls = $('<div>');
        headerControls.append(
          $('<button>')
            .addClass('button delete-btn far fa-trash-alt')
            .attr('tabindex', '-1')
            .attr('data-token-id', response.data['new_token_id']),
        );
        headerControls.append($('<input>').attr('type', 'checkbox'));
        tokenHeader.append(headerControls);

        const tokenInfoContainer = $('<div>').addClass('token-info-container');
        const tokenInfo = $('<div>').addClass('token-info');
        tokenInfo.append($('<span>').addClass('icon fas fa-calendar-alt'));
        tokenInfo.append($('<span>').text('Expires on:'));
        tokenInfo.append(
          $('<span>')
            .addClass('date')
            .text(response.data['new_token_expires_at']),
        );
        tokenInfoContainer.append(tokenInfo);

        const tokenDetails = $('<div>').addClass('token-details');
        tokenDetails.append(
          $('<input>')
            .addClass('token-value')
            .attr('type', 'text')
            .val(response.data['new_token_secret'])
            .prop('readonly', true),
        );
        tokenDetails.append(
          $('<button>')
            .addClass('button copy-btn far fa-copy')
            .attr('tabindex', '-1')
            .attr('data-clipboard-text', response.data['new_token_secret']),
        );

        tokenCard.append(tokenHeader, tokenInfoContainer, tokenDetails);
        tokenCard.append(
          $('<p>')
            .addClass('copy-message')
            .text(
              'Make sure to copy your personal access token now as you will not be able to see this again.',
            ),
        );

        li.append(tokenCard);

        // Update DOM safely
        $('.error-message').empty();
        $('.token-name-input').val('');
        $('.generate-token-btn').prop('disabled', true);
        $('.pat-list').append(li);
        Pontoon.endLoader('Token created.');
      },
      error: function (response) {
        const errors = response.responseJSON.errors;

        $('.error-message').html('');

        for (const error in errors) {
          const errorMessages = errors[error].join(', ');
          $(`.error-message`).append($('<p>').text(errorMessages));
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
      success: function (response) {
        if (response.status === 'success') {
          $(`li[data-token-id="${tokenId}"]`).remove();
        }
      },
      error: function () {
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
      url: '/api/v1/user/' + $('#profile input[name="username"]').val() + '/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('body').data('csrf'),
        attribute: self.data('attribute'),
        value: !self.is('.enabled'),
      },
      success: function () {
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
      error: function (request) {
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
      success: function (data) {
        if (data === 'ok') {
          Pontoon.endLoader('Custom homepage saved.');
        }
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
      success: function (data) {
        if (data === 'ok') {
          Pontoon.endLoader('Preferred source locale saved.');
        }
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
