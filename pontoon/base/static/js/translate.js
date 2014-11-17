$(function() {

  function mouseUpHandler(e) {
    $(document)
      .unbind('mousemove', mouseMoveHandler)
      .unbind('mouseup', mouseUpHandler);

    $('#iframe-cover').hide(); // iframe fix
    $('#editor:not(".opened")').css('left', $('#sidebar').width()).show();

    var initial = e.data.initial,
        advanced = Pontoon.app.advanced;
    if (initial.advanced !== advanced) {

      // On switch to 2-column view, populate editor if empty
      if (advanced) {
        if (!$('#editor')[0].entity || !$('#entitylist .entity.hovered').length) {
          $("#entitylist .entity:first").mouseover().click();
        }

      // On switch to 1-column view, open editor if needed
      } else {
        if ($('#entitylist .entity.hovered').length) {
          Pontoon.openEditor($('#editor')[0].entity);
        }
      }
    }
  }

  function mouseMoveHandler(e) {
    var initial = e.data.initial,
        left = Math.min(Math.max(initial.leftWidth + (e.pageX - initial.position), initial.leftMin), initial.leftMax),
        right = Math.min(Math.max(initial.rightWidth - (e.pageX - initial.position), 0), initial.leftMax - initial.leftMin);

    initial.left.width(left);
    initial.right.width(right).css('margin-left', left);

    // Sidebar resized over 2-column breakpoint
    if (left >= 700) {
      $('#entitylist, #editor').removeAttr('style');
      if (!Pontoon.app.advanced) {
        Pontoon.app.advanced = true;
        initial.left.addClass('advanced');
        $('#editor')
          .addClass('opened')
          .show();
      }

    // Sidebar resized below 2-column breakpoint
    } else {
      if (Pontoon.app.advanced) {
        Pontoon.app.advanced = false;
        initial.left.removeClass('advanced').show();
        $('#editor')
          .removeClass('opened')
          .css('left', $('#sidebar').width())
          .hide();
      }
    }

    $('#iframe-cover').width(right).css('margin-left', left); // iframe fix
  }

  function resizeIframe() {
    $('#source')
      .width($(window).width() - $('#sidebar:visible').width())
      .height($(window).height() - $('#pontoon > header').outerHeight());
  }

  function attachResizeHandlers() {
    // Resize iframe with window
    $(window).resize(function () {
      resizeIframe();
      Pontoon.common.postMessage("RESIZE");
    });

    // Resize sidebar and iframe
    $('#drag').bind('mousedown', function (e) {
      e.preventDefault();

      var left = $('#sidebar'),
          right = $('#source'),
          data = {
            left: left,
            right: right,
            leftWidth: left.width(),
            rightWidth: right.width(),
            leftMin: 350,
            leftMax: $(window).width(),
            position: e.pageX,
            advanced: Pontoon.app.advanced
          };

      $('#iframe-cover').show().width(right.width()); // iframe fix
      $('#editor:not(".opened")').hide();

      $(document)
        .bind('mousemove', { initial: data }, mouseMoveHandler)
        .bind('mouseup', { initial: data }, mouseUpHandler);
    });
  }

  function initializeWithoutWebsite() {
    $('#pontoon > header').show();
    $('#sidebar')
      .addClass('advanced')
      .css('width', '100%');
    $('#switch, #drag').remove();
    $('#editor').addClass('opened');
    $('#project-load').hide();

    Pontoon.init(window, true);
  }

  function receiveMessage(e) {
    if (e.source === projectWindow) {
      if (JSON.parse(e.data).type === "READY") {
        window.removeEventListener("message", receiveMessage, false);
        $('#pontoon > header').show();

        var advanced = false,
            websiteWidth = $('#server').data('width');

        if (websiteWidth) {
          var windowWidth = $(window).width(),
              sidebarWidth = windowWidth - websiteWidth;

          if (sidebarWidth >= 700) {
            advanced = true;
            $('#sidebar').addClass('advanced').width(sidebarWidth);
            $('#switch, #editor').addClass('opened');

          } else {
            $('#sidebar').show().width(sidebarWidth);
            $('#switch').addClass('opened');
            $('#editor').css('left', sidebarWidth);
          }
        }

        $('#source').show().css('margin-left', $('#sidebar:visible').width());
        resizeIframe();
        $('#project-load').hide();
        Pontoon.init(window, advanced, projectWindow);
      }
    }
  }

  var url = $('#server').data('url');

  // Initialize Pontoon for projects without in place translation support
  if (!url) {
    return initializeWithoutWebsite();
  }

  // Initialize Pontoon for projects with in place translation support
  $('#source').attr('src', url);
  var projectWindow = $('#source')[0].contentWindow;
  window.addEventListener("message", receiveMessage, false);

  var i = 0,
      interval = setInterval(function() {
        if (i < 100) {
          i++;
          // Set in Pontoon.init(), which is called on READY
          if (Pontoon.app) {
            clearInterval(interval);
            return attachResizeHandlers();
          }
        } else {
          // If no READY call in 10 seconds
          clearInterval(interval);
          $('#source, #iframe-cover, #not-on-page, #profile .html').remove();
          window.removeEventListener("message", receiveMessage, false);
          return initializeWithoutWebsite();
        }
      }, 100);
});
