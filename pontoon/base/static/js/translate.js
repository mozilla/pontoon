$(function() {

  function mouseUpHandler() {
    $(document)
      .unbind('mousemove', mouseMoveHandler)
      .unbind('mouseup', mouseUpHandler);

    $('#iframe-cover').hide(); // iframe fix
    $('#editor:not(".active")').css('left', $('#sidebar').width()).show();
  };

  function mouseMoveHandler(e) {
    var initial = e.data.initial,
        left = Math.min(Math.max(initial.leftWidth + (e.pageX - initial.position), initial.leftMin), initial.leftMax),
        right = Math.min(Math.max(initial.rightWidth - (e.pageX - initial.position), 0), initial.leftMax - initial.leftMin);

    initial.left.width(left);
    initial.right.width(right).css('margin-left', left);

    $('#iframe-cover').width(right).css('margin-left', left); // iframe fix
  };

  function resizeIframe() {
    $('#source').width($(window).width() - $('#sidebar:visible').width())
      .height($(window).height() - $('#pontoon > header').outerHeight());
  }

  function receiveMessage(e) {
    // TODO: Check origin - hardcode Pontoon domain name
    if (JSON.parse(e.data).type === "SUPPORTED") {

      $('#pontoon > header').slideDown(function() {
        if (advanced) {
          $('#sidebar').addClass('advanced');
          $('#switch').addClass('opened');
        }

        $('#source').show().css('margin-left', $('#sidebar:visible').width());
        resizeIframe();
        $('#project-load').hide();
      });

      Pontoon.init(window, projectWindow);
      window.removeEventListener("message", receiveMessage, false);
    }
  }

  var url = $('#server').data('url'),
      advanced = $('#server').data('external');

  // Initialize Pontoon if project code supports it
  $('#source').attr('src', url);
  projectWindow = $('#source')[0].contentWindow;
  window.addEventListener("message", receiveMessage, false);

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
              locale = $('#server').data('locale'),
              escapedLocale = locale.replace(".", "\\.").replace("@", "\\@"),
              errorLink = (lang ? '/' + lang : '') + '/translate/error/?locale=' + escapedLocale + '&url=' + url + (url[url.length-1] !== '/' ? '/' : '');
          window.location = errorLink + '&error=' + "Oops, website is not supported by Pontoon.";
        }
      }, 100);

  // Resize iframe with window
  $(window).resize(function () {
    resizeIframe();
    Pontoon.common.postMessage("RESIZE");
  });

  // Resize sidebar and iframe
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
    $('#editor:not(".active")').hide();

    $(document)
      .bind('mousemove', { initial: data }, mouseMoveHandler)
      .bind('mouseup', { initial: data }, mouseUpHandler);
  });
});
