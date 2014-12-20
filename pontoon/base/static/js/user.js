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
  var block = $('#timeline > .container > div');
  block.each(function() {
    if ($(this).offset().top > $(window).scrollTop() + $(window).height() * 0.75) {
      $(this).find('.tick, .content').addClass('is-hidden');
    }
  });

  //on scolling, show/animate timeline blocks when enter the viewport
  $(window).on('scroll', function() {
    block.each(function() {
      if ($(this).offset().top <= $(window).scrollTop() + $(window).height() * 0.75 && $(this).find('.tick').hasClass('is-hidden')) {
        $(this).find('.tick, .content').removeClass('is-hidden').addClass('bounce-in');
      }
    });
  });

});
