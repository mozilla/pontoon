$(function() {

  var input = $('#subtitle input');

  // Save user name handler
  function save() {
    $.ajax({
      url: 'save-user-name/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('#server').data('csrf'),
        name: $.trim(input.val())
      },
      success: function(data) {
        if (data === "ok") {
          input.blur();
          Pontoon.endLoader('Thank you!');
        } else if (data === "length") {
          Pontoon.endLoader('Must be between 3 and 30 characters.', 'error');
        } else {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        }
      },
      error: function() {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      }
    });
  }

  // Save user name by mouse or keyboard
  $('.submit').click(function() {
    save();
  });
  input.keydown(function(e) {
    if (e.which === 13) {
      e.preventDefault();
      save();
    }
  });

});
