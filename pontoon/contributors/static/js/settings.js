$(function() {
  $('#homepage .locale .menu li:not(".no-match")').click(function () {
    var custom_homepage = $(this).find('.language').data('code');

    $.ajax({
      url: '/save-custom-homepage/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('#server').data('csrf'),
        custom_homepage: custom_homepage
      },
      success: function(data) {
        if (data === 'ok') {
          Pontoon.endLoader('Custom homepage saved.');
        }
      },
      error: function(request) {
        if (request.responseText === 'error') {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
      }
    });
  });

  // Show a warning when a user changes their email address.
  var emailField = $('#id_email');
  var warningContent = $('#email-warning');
  var originalEmail = emailField.val();

  emailField.on('keyup', function () {
    var newEmail = emailField.val();
    if (newEmail === originalEmail && warningContent.is(':visible')) {
      warningContent.hide();
    }
    else if (newEmail !== originalEmail && !warningContent.is(':visible')) {
      warningContent.show();
    }
  });
});
