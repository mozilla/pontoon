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

  $('.url').val(url);
  $('.locale .button .language').addClass(escapedLocale).html($('.locale .menu .language.' + escapedLocale).html());
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
    /*
    if (e.data.initial.below.height() === 0) {
      $('#main').removeClass('opened');
      Pontoon.common.postMessage("MODE", "Advanced");
    } else {
      $('#main').addClass('opened');
      Pontoon.common.postMessage("MODE", "Basic");
    }
    */
  };
  $('#drag').bind('mousedown', function(e) {
    e.preventDefault();

    var up = $('#source'),
        below = $('#sidebar'),
        data = {
          up: up,
          below: below,
          uHeight: up.height(),
          bHeight: below.height(),
          offTop: e.pageY,
          min: 0,
          max: $(document).height() - $("#pontoon > header").outerHeight()
        };

    // iframe fix: Prevent iframes from capturing the mousemove events during a drag
    $('#iframe-cover').show().height(up.height());

    $(document)
      .bind('mousemove', { initial: data }, mouseMoveHandler)
      .bind('mouseup', { initial: data }, mouseUpHandler);
  });

});
