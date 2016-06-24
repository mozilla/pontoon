$(function() {

  var input = $('#subtitle input');

  // Save user name handler
  function save() {
    $.ajax({
      url: '/save-user-name/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('#server').data('csrf'),
        first_name: $.trim(input.val())
      },
      success: function(data) {
        if (data === "ok") {
          input.blur();
          Pontoon.endLoader('Thank you!');
        };
      },
      error: function(request) {
        if (request.responseText === "error") {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        } else {
          Pontoon.endLoader(request.responseText, 'error');
        }
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

  // Show/animate timeline blocks inside viewport
  function animate() {
    blocks.each(function() {
      var block_bottom = $(this).offset().top + $(this).outerHeight(),
          window_bottom = $(window).scrollTop() + $(window).height();

      if (block_bottom <= window_bottom) {
        $(this).find('.tick, .content')
          .css('visibility', 'visible').addClass(function() {
            return (blocks.length > 1) ? 'bounce-in' : '';
          });
      }
    });
  }

  var blocks = $('#timeline > .container > div');
  animate();
  $(window).on('scroll', animate);

  if ($('.notification li').length) {
    Pontoon.endLoader();
  }

});
