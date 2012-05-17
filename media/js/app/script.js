// remap jQuery to $
(function($) {

  $(function() {

    // Resizable
	  var mouseMoveHandler = function(e) {
	    var initial = e.data.initial,
          u = Math.min(Math.max(initial.uHeight + (e.pageY - initial.offTop), initial.min), initial.max),
          b = Math.min(Math.max(initial.bHeight - (e.pageY - initial.offTop), initial.min), initial.max);
      initial.up.height(u);
      initial.below.height(b);

      $('#iframe-cover').height(initial.up.height()); // iframe fix
    };
    var mouseUpHandler = function(e) {
      $(document)
        .unbind('mousemove', mouseMoveHandler)
        .unbind('mouseup', mouseUpHandler);

      $('#iframe-cover').hide(); // iframe fix
      if (e.data.initial.below.height() === 0) {
        $('#main').removeClass('opened');
        Pontoon.common.postMessage("MODE", "Advanced");
      } else {
        $('#main').addClass('opened');
        Pontoon.common.postMessage("MODE", "Basic");
      }      
    };
	  $('#logo, #drag').bind('mousedown', function(e) {
      e.preventDefault();

      var up = $('#source'),
          below = $('#entitylist'),
          data = {
            up: up,
            below: below,
            uHeight: up.height(),
            bHeight: below.height(),
            offTop: e.pageY,
            min: 0,
            max: $(document).height()
          };

      // iframe fix: Prevent iframes from capturing the mousemove events during a drag
      $('#iframe-cover').show().height(up.height());

      $(document)
        .bind('mousemove', { initial: data }, mouseMoveHandler)
        .bind('mouseup', { initial: data }, mouseUpHandler);
    });

    // Resize iframe with window
    $(window).resize(function () {
      $('#source').height($(document).height() - $('#main').height());
    });

    // Validate URL
    function checkURL() {
      // Initialize Pontoon only if project code supports it
      function receiveMessage(e) {
        // TODO: Check origin - hardcode Pontoon domain name
        if (JSON.parse(e.data).type === "SUPPORTED") {
          // Slide up intro page, show header and iframe with appropriate height
          $('#intro').slideUp(function() {
            $('#source').show();
            $('#main').slideDown(function() {
              $('#source').height($(document).height() - $(this).height());
            });
            Pontoon.init(window, $('#source').get(0).contentWindow, locale);
          });
          window.removeEventListener("message", receiveMessage, false);
        }
      }
      window.addEventListener("message", receiveMessage, false);

      // Load project page into iframe
      $('#source').attr('src', url);
      $('#intro .notification')
        .html('Loading...')
        .addClass('message').removeClass('error')
        .css('visibility', 'visible');

      // Show error message if no callback for 5 seconds: Pontoon/iframe not supported, 404…
      var i = 0,
          callback = setInterval(function() {
            if (i < 50) {
              i++;
              if (Pontoon._doc) { // Set in Pontoon.init() which is called on "supported"
                clearInterval(callback);
              }
            } else {
              clearInterval(callback);
              $('#intro .notification')
                .html('Oops, website is either not supported by Pontoon or could not be found.')
                .addClass('error').removeClass('message')
                .css('visibility', 'visible');
            }
          }, 100);
    }

    // Update locale selector
    function updateLocale(locale) {
      if (!locale || $('.locale .menu .flag.' + locale).length === 0) {
        locale = $("#intro .menu .flag:first").attr("class").split(" ")[1];
      }
      $('.locale .button')
        .find('.flag').addClass(locale).end()
        .find('.language').html($('.locale .menu .flag.' + locale).siblings('.language').html());
      if (url) {
        checkURL();
      }
    }

    // Set locale using Accept-Language header
    function guessLocale() {
      updateLocale($('#server').data('language'));
    }

    // Validate locale
    function isValidLocale(locale) {
      var valid = false;
      $("#intro .menu .flag").each(function() {
        if (locale === $(this).attr("class").split(" ")[1]) {
          valid = true;
        }
      });
      return valid;
    }

    // MAIN CODE

    // Empty iframe if cached
    $('#source').removeAttr("src");

    // Check for params
    var locale = $('#server').data('locale'),
        url = $('#server').data('url');

    // Translate
    if (locale && url) {
      $('.url').val(url);
      // Set locale
      if (isValidLocale(locale)) {
        updateLocale(locale);
      } else {
        guessLocale();
      }

    // Intro
    } else {
      guessLocale();
      // Set include script URL
      $("#install")
        .find("code").html('&lt;script src="' + window.location.href + 'media/js/project/pontoon.js"&gt;&lt;/script&gt;')
        .end().css("visibility", "visible");
      $("#intro").css("display", "table");
    }

  });

}(this.jQuery));

// usage: log('inside coolFunc',this,arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function() {
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if (this.console) {
    console.log(Array.prototype.slice.call(arguments));
  }
};

// catch all document.write() calls
(function(doc) {
  var write = doc.write;
  doc.write = function(q) {
    log('document.write(): ', arguments);
    if (/docwriteregexwhitelist/.test(q)) {
      write.apply(doc,arguments);
    }
  };
}(document));
