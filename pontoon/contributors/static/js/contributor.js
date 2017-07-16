$(function() {

  var username = $('#profile-username');
  var email = $('#profile-email');

  // Save user profile handler
  function save() {
    $.ajax({
      url: '/save-user-profile/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('#server').data('csrf'),
        first_name: $.trim(username.val()),
        email: $.trim(email.val())
      },
      success: function(data) {
        if (data === "ok") {
          Pontoon.endLoader('Thank you!');
        }
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

  // Save user profile by mouse or keyboard
  $('.submit').click(function() {
    save();
  });
  username.keydown(function(e) {
    if (e.which === 13) {
      e.preventDefault();
      save();
    }
  });
  email.keydown(function(e) {
    if (e.which === 13) {
      e.preventDefault();
      save();
    }
  });

  function loadNextEvents(cb) {
    var currentPage = $timeline.data('page'),
      nextPage = parseInt(currentPage, 10) + 1,

      // Determines if client should request new timeline events.
      finalized = parseInt($timeline.data('finalized'), 10);

    if (finalized || $timelineLoader.is(':visible')) {
      return;
    }

    $timelineLoader.show();

    $.get(timelineUrl, {page: nextPage}).then(
      function (timelineContents) {
        $('#main > .container').append(timelineContents);
        $timelineLoader.hide();
        $timeline.data('page', nextPage);
        cb();
      },
      function (response) {
        $timeline.data('page', nextPage);
        if (response.status === 404) {
          $timeline.data('finalized', 1);
          cb();
        } else {
          Pontoon.endLoader("Couldn't load the timeline.");
        }
        $timelineLoader.hide();
      }
    );
  }

  // Show/animate timeline blocks inside viewport
  function animate() {
    var $blocks = $('#main > .container > div');

    $blocks.each(function() {
      var block_bottom = $(this).offset().top + $(this).outerHeight(),
          window_bottom = $(window).scrollTop() + $(window).height(),
          blockSelf = this;

      // Animation of event that's displayed on the user timeline.
      function showEvent() {
        $(this).find('.tick, .content')
          .css('visibility', 'visible').addClass(function() {
          return ($blocks.length > 1) ? 'bounce-in' : '';
        });
      }

      if (block_bottom <= window_bottom) {
        if (($blocks.index($(this)) === $blocks.length - 1)) {
          loadNextEvents(function() {
            showEvent.apply(blockSelf);
          });
        } else {
          showEvent.apply(blockSelf);
        }
      }
    });
  }

  var $timelineLoader = $('#timeline-loader'),
      $timeline = $('#main'),
      timelineUrl = $timeline.data('url');

  // The first page of events.
  loadNextEvents(function() {
    $(window).scroll();
  });

  $(window).on('scroll', animate);

  if ($('.notification li').length) {
    Pontoon.endLoader();
  }

});
