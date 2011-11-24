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
        Pontoon.common.postMessage("mode", "Advanced");
      } else {
        $('#main').addClass('opened');
        Pontoon.common.postMessage("mode", "Basic");
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
        if (JSON.parse(e.data).type === "supported") {
          // Slide up intro page and show iframe
          $('#intro').slideUp("slow", function() {
            $('#source').show();
            Pontoon.init($('#source').get(0).contentWindow, document, locale);
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

    // Set locale using browser language detection
    // TODO: develop internal solution
    // Source: http://stackoverflow.com/questions/1043339/javascript-for-detecting-browser-language-preference
    function guessLocale() {
      $.ajax({ 
        url: "http://ajaxhttpheaders.appspot.com", 
        dataType: 'jsonp', 
        success: function(headers) {
          var locale = headers['Accept-Language'].substring(0, 2),
              entry = $('#intro .locale .menu .flag.' + locale);
          updateLocale(locale);
        },
        error: function() {
          updateLocale();
        }
      });
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



    // Main code

    // Check for params
    var locale = window.location.search.split("&locale=")[1] || "",
        temp = window.location.search.split("?url=")[1],
        url = temp ? temp.split("&locale=")[0] : "";
    $('.url').val(url);

    // Empty iframe if cached, prepare size and resize it with window
    $('#source').removeAttr("src").height($(document).height() - $('#main').height());

    // Set locale
    if (isValidLocale(locale)) {
      updateLocale(locale);
    } else {
      guessLocale();
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
