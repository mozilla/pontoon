// remap jQuery to $
(function($) {

  $(function() {
    // Empty iframe if cached
    $("iframe").attr("src", "about:blank");

	// Prepare iframe size and resize it with window
    $('#source').height($(document).height() - $('#pontoon').height());
    $(window).resize(function () {
      $('#source').height($(document).height() - $('#pontoon').height());
    });

    // Load website into iframe
    $('.url').keypress(function (e) {
      var code = (e.keyCode ? e.keyCode : e.which);
      if (code === 13) {
        $('#intro').slideUp("fast", function() {

          // TODO: use real URLs
          $('#source').attr('src', /*$('.url').val()*/ window.location.href.split("client/www")[0] + 'projects/testpilot');
          $('#pontoon .url').val(/*$('.url').val()*/ window.location.href.split("client/www")[0] + 'projects/testpilot');
        });

        $('#source').unbind("load.pontoon").bind("load.pontoon", function() {
          // Quit if website not specified
          if (!$(this).attr('src')) {
            return;
          }

          // Initialize Pontoon
          Pontoon.init(this.contentDocument, document);
        });
      }
    });

    // Click on a test pilot link
    $('#test-pilot').click(function() {
      var event = $.Event("keypress");
      event.which = 13;
      $("#intro .url").trigger(event);
    });

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

      $('#iframe-cover').remove(); // iframe fix
    };
	$('#pontoon header').bind('mousedown', function(e) {
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
      up.after('<div id="iframe-cover" style="height:' + up.height() + 'px"></div>');

      $(document)
        .bind('mousemove', { initial: data }, mouseMoveHandler)
        .bind('mouseup', mouseUpHandler);
    });

	// Generate bookmarklet
    var publicDomain = window.location.href.split("client/www/")[0]; // Transfer public folder location to the bookmarklet
    $("#bookmarklet").attr("href", "javascript:(function(d){if(typeof Pontoon==='undefined'){PontoonBookmarklet='" + publicDomain + "';d.body.appendChild(d.createElement('script')).src=PontoonBookmarklet+'/client/bookmarklet/loader.js';}})(document)");

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
