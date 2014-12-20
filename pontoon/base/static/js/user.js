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
    if ($(this).css('opacity') === "0") {
      return;
    }
    save();
  });
  input.keydown(function(e) {
    if (e.which === 13) {
      e.preventDefault();
      save();
    }
  });

  // Hide timeline blocks outside viewport
  var blocks = $('#timeline > .container > div');
  blocks.each(function() {
    var block_bottom = $(this).offset().top + $(this).outerHeight(),
        window_bottom = $(window).scrollTop() + $(window).height();

    if (block_bottom > window_bottom) {
      $(this).find('.tick, .content').addClass('is-hidden');
    }
  });

  // Show/animate timeline blocks when entering the viewport on scroll
  $(window).on('scroll', function() {
    blocks.each(function() {
      var block_bottom = $(this).offset().top + $(this).outerHeight(),
          window_bottom = $(window).scrollTop() + $(window).height(),
          hidden = $(this).find('.tick').hasClass('is-hidden');

      if (block_bottom <= window_bottom && hidden) {
        $(this).find('.tick, .content')
          .removeClass('is-hidden').addClass('bounce-in');
      }
    });
  });

});
