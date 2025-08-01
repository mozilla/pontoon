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

  $('.generate-token').click(function (e) {
    e.preventDefault();

    const csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
      url: '/generate-token/',
      type: 'POST',
      data: {
        name: $('.id_name').val(),
        csrfmiddlewaretoken: csrfmiddlewaretoken,
      },
      success: function (response) {
        // console.log(response.data);
        if (response.status === 'success') {
          const lastListItem = $('.pat-list li:last');
          const newListItem = lastListItem.clone();

          newListItem.attr('data-token-id', response.data['new_token_id']);
          newListItem.addClass('created');
          newListItem.find('.token-name').text(response.data['new_token_name']);
          newListItem
            .find('.token-date .date')
            .first()
            .text(response.data['new_token_expires_at']);
          newListItem
            .find('.token-date .date')
            .last()
            .text(
              response.data['new_token_last_used']
                ? response.data['new_token_last_used']
                : 'Never',
            );
          newListItem
            .find('.delete-btn')
            .attr('data-token-id', response.data['new_token_id']);

          const tokenInfo = newListItem.find('.token-info');
          const newItem = $('<div class="new-item">New item content</div>');
          tokenInfo.after(newItem);
          $('.pat-list').append(newListItem);
        }
      },
    });
  });

  $('.delete-btn').click(function (e) {
    e.preventDefault();

    const tokenId = $(this).data('token-id');
    // const tokenId = $(this).parents('li').data('token-id');
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
    });
  });

  $('.id_name').on('input', function () {
    if ($(this).val().trim() !== '') {
      $('.generate-token').prop('disabled', false); // Enable the button
    } else {
      $('.generate-token').prop('disabled', true); // Disable the button
    }
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
