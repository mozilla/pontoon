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
      
          // Remove any existing pontoon clients
          // TODO: do we need this?
          if (Pontoon._clients.length) {
            Pontoon._clients = [];
          }
      
          // Turn on Pontoon client
          var doc = this.contentDocument,
              pc = new Pontoon.client(doc, document);
          pc.turnOn(pc, doc);
        });
      }
    });
    
    // Click on a test pilot link
    $('#test-pilot').click(function() {
      var event = $.Event("keypress");
      event.which = 13;
      $("#intro .url").trigger(event);
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
