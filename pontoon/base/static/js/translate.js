$(function() {

  var url = $('#server').data('url'),
      locale = $('#server').data('locale'),
      advanced = $('#server').data('external'),
      escapedLocale = locale.replace(".", "\\.").replace("@", "\\@"),
      projectWindow = null;

  // Resize iframe with window
  $(window).resize(function () {
    $('#source').width($(window).width() - $('#sidebar:visible').width())
                .height($(window).height() - $('#pontoon > header').outerHeight());
    Pontoon.common.postMessage("RESIZE");
  });

  // Empty iframe if cached
  $('#source').removeAttr("src");

  // Initialize Pontoon only if project code supports it
  function receiveMessage(e) {

    // TODO: Check origin - hardcode Pontoon domain name
    if (JSON.parse(e.data).type === "SUPPORTED") {
      $('#pontoon > header').slideDown(function() {

        // Open advanced features by default if project requests them
        if (advanced) {
          $('#sidebar').addClass('advanced');
          $('#switch').addClass('opened');
        }

        $('#source').show().width($(window).width() - $('#sidebar:visible').width())
                           .height($(window).height() - $(this).outerHeight())
                           .css('margin-left', $('#sidebar:visible').width());
        $('#project-load').hide();
      });

      Pontoon.init(window, projectWindow, locale);
      window.removeEventListener("message", receiveMessage, false);
    }
  }
  window.addEventListener("message", receiveMessage, false);

  $('#source').attr('src', url);
  projectWindow = $('#source')[0].contentWindow;

  // Show error message if no callback for 30 seconds: Pontoon/iframe not supported, 404…
  var i = 0,
      interval = setInterval(function() {
        if (i < 300) {
          i++;
          if (Pontoon.app) { // Set in Pontoon.init() which is called on "supported"
            clearInterval(interval);
          }
        } else {
          clearInterval(interval);
          var lang = $('html').attr('lang'),
              errorLink = (lang ? '/' + lang : '') + '/translate/error/?locale=' + escapedLocale + '&url=' + url + (url[url.length-1] !== '/' ? '/' : '');
          window.location = errorLink + '&error=' + "Oops, website is not supported by Pontoon.";
        }
      }, 100);

  // Resizable
  var mouseMoveHandler = function(e) {
    var initial = e.data.initial,
        left = Math.min(Math.max(initial.leftWidth + (e.pageX - initial.position), initial.leftMin), initial.leftMax),
        right = Math.min(Math.max(initial.rightWidth - (e.pageX - initial.position), 0), initial.leftMax - initial.leftMin);

    initial.left.width(left);
    initial.right.width(right).css('margin-left', left);

    $('#iframe-cover').width(right).css('margin-left', left); // iframe fix
  };

  var mouseUpHandler = function(e) {
    $(document)
      .unbind('mousemove', mouseMoveHandler)
      .unbind('mouseup', mouseUpHandler);

    $('#iframe-cover').hide(); // iframe fix
  };

  $('#drag').bind('mousedown', function(e) {
    e.preventDefault();

    var left = $('#sidebar'),
        right = $('#source'),
        data = {
          left: left,
          right: right,
          leftWidth: left.width(),
          rightWidth: right.width(),
          leftMin: 450,
          leftMax: $(window).width(),
          position: e.pageX
        };

    $('#iframe-cover').show().width(right.width()); // iframe fix

    $(document)
      .bind('mousemove', { initial: data }, mouseMoveHandler)
      .bind('mouseup', { initial: data }, mouseUpHandler);
  });

});
