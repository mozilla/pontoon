$(function() {

  function mouseUpHandler() {
    $(document)
      .unbind('mousemove', mouseMoveHandler)
      .unbind('mouseup', mouseUpHandler);

    $('#iframe-cover').hide(); // iframe fix
    $('#editor:not(".opened")').css('left', $('#sidebar').width()).show();
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
    if (e.source === projectWindow) {
      if (JSON.parse(e.data).type === "READY") {

        $('#pontoon > header').slideDown(function() {
          var websiteWidth = $('#server').data('width');

          if (websiteWidth) {
            var windowWidth = $(window).width(),
                sidebarWidth = windowWidth - websiteWidth;

            if (sidebarWidth >= 900) {
              $('#sidebar').addClass('advanced').width(sidebarWidth);
              $('#switch, #editor').addClass('opened');

            } else if (sidebarWidth >= 450) {
              $('#sidebar').show().width(sidebarWidth);
              $('#switch').addClass('opened');
              $('#editor').css('left', sidebarWidth);
            }
          }

          $('#source').show().css('margin-left', $('#sidebar:visible').width());
          resizeIframe();
          $('#project-load').hide();
        });

        Pontoon.init(window, projectWindow);
        window.removeEventListener("message", receiveMessage, false);
      }
    }
  }

  var url = $('#server').data('url');

  // Initialize Pontoon for projects without in-place translation support
  if (!url) {
    $('#pontoon > header').slideDown(function() {
      $('#sidebar')
        .addClass('advanced')
        .css('width', '100%');
      $('#switch, #drag').remove();
      $('#editor').addClass('opened');
      $('#project-load').hide();
    });

    return Pontoon.init(window);
  }

  // Initialize Pontoon for projects with in-place translation support
  $('#source').attr('src', url);
  var projectWindow = $('#source')[0].contentWindow;
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
              project = $('#server').data('id'),
              errorLink = (lang ? '/' + lang : '') + '/translate/error/?locale=' + escapedLocale + '&project=' + project;
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
          leftMin: ($('#server').data('width') && ($(window).width() - $('#server').data('width')) >= 900) ? 900 : 450,
          leftMax: $(window).width(),
          position: e.pageX
        };

    $('#iframe-cover').show().width(right.width()); // iframe fix
    $('#editor:not(".opened")').hide();

    $(document)
      .bind('mousemove', { initial: data }, mouseMoveHandler)
      .bind('mouseup', { initial: data }, mouseUpHandler);
  });
});
