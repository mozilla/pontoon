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
      } else {
      	$('#main').addClass('opened');
      }
    };
	$('#logo').bind('mousedown', function(e) {
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

    // Prepare iframe size and resize it with window
    $('#source').height($(document).height() - $('#main').height());
    $(window).resize(function () {
      $('#source').height($(document).height() - $('#main').height());
    });

    // Selector handler
    $('.selector').unbind("click.pontoon").bind("click.pontoon", function(e) {
      $(this).siblings('.menu').toggle();
      $(this).parents('.select').toggleClass('opened');
    });

    // Locale selector
    $('.locale .menu li:not(".add")').unbind("click.pontoon").bind("click.pontoon", function() {
      // TODO: url and locale validation
      window.location = "?url=" + $('#intro .url').val() + "&locale=" + $(this).find('.flag').attr('class').split(' ')[1];
    });

    // Update locale selector
    function updateLocale(locale) {
      var l = locale || 'de';
      $('.locale')
        .find('.button')
          .find('.flag').addClass(l).end()
          .find('.language').html($('.locale .menu .flag.' + l).siblings('.language').html()).end().end()
        .find('.handle').html(' &#9652;');
    }

    // When website loaded, initialize Pontoon
    $('#source').unbind("load.pontoon").bind("load.pontoon", function() {
      if (!$(this).attr('src')) {
        return;
      }
      Pontoon.init(this.contentDocument, document, "sl");
    });

    // Empty iframe if cached
    $("#source").removeAttr("src");

    // Check for params
    var locale = window.location.search.split("&locale=")[1] || "",
        temp = window.location.search.split("?url=")[1],
        website = temp ? temp.split("&locale=")[0] : "";

    if (website.length > 0 && locale.length > 0) {
      // TODO: use real params
      website = "projects/testpilot";
      locale = null;

      $('#intro').slideUp("fast", function() {
        $('#source').attr('src', website);
        $('#main .url').val(website);
        updateLocale(locale);
      });
    } else {
      /*
       * Set locale using browser language detection
       * TODO: develop internal solution
       *
       * Source: http://stackoverflow.com/questions/1043339/javascript-for-detecting-browser-language-preference
      */
      $.ajax({ 
        url: "http://ajaxhttpheaders.appspot.com", 
        dataType: 'jsonp', 
        success: function(headers) {
          var locale = headers['Accept-Language'].substring(0, 2),
              entry = $('#intro .locale .menu .flag.' + locale);
          if (entry.length !== 0) {
            updateLocale(locale);
          } else {
            updateLocale();
          }
        },
        error: function() {
          updateLocale();
        }
      });
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
