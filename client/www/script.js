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
      $(this).toggleClass('opened');
    });

    // Locale selector
    $('.locale .menu li:not(".add")').unbind("click.pontoon").bind("click.pontoon", function() {
      $('.locale .selector .flag').attr("class", $(this).find('span').attr("class"));
      $('.locale .selector .language').html($(this).find('.language').html());
      $('.locale .selector').click();
    });

    function loadIframeContents(code) {
      var website = window.location.search.split("?url=")[1] || "";
      if (website.length > 0) {
        $('#intro').slideUp("fast", function() {
          // TODO: use real URLs
          $('#source').attr('src', /* website */ 'projects/testpilot');
          $('#main .url').val(/* website */ 'projects/testpilot');
        });

        $('#source').unbind("load.pontoon").bind("load.pontoon", function() {
          // Quit if website not specified
          if (!$(this).attr('src')) {
            return;
          }
          // Initialize Pontoon
          Pontoon.init(this.contentDocument, document, code);
        });
        
      } else {
	    // Empty iframe if cached
  	    $("#source").attr("src", "about:blank");
      }
    }

    function updateLocale(code, name) {
      $('.locale .selector')
        .find('.flag').addClass(code).removeClass('blank').end()
        .find('.language').html(name).end()
        .find('.handle').html(' &#9652;').end();
      
      loadIframeContents(code);
    }

    /*
     * Set locale using browser language detection
     * TODO: develop internal solution
     *
     * Browser language cannot be generally obtained via navigator.language
     * Using HTTP 'Accept-Language' header via external service temporary
     * Source: http://stackoverflow.com/questions/1043339/javascript-for-detecting-browser-language-preference
    */
    $.ajax({ 
      url: "http://ajaxhttpheaders.appspot.com", 
      dataType: 'jsonp', 
      success: function(headers) {
        var locale = headers['Accept-Language'].substring(0, 2),
            entry = $('#intro .locale .menu .flag.' + locale);
        if (entry.length !== 0) {
          updateLocale(locale, entry.next().text());
        } else {
          updateLocale('de', 'Deutsch');
        }
      },
      error: function() {
        updateLocale('de', 'Deutsch');
      }
    });
      
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
