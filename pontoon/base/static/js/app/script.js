// remap jQuery to $
(function($) {

  $(function() {

    /*** MAIN CODE ***/

    var base = $('base').attr('href'),
        l = window.location;

    // Resize iframe with window
    $(window).resize(function () {
      $('#source').height($(document).height() - $('#main').height());
    });

    // Empty iframe if cached
    $('#source').removeAttr("src");

    // Set Demo URL
    $('#demo').attr('href', '/locale/de/project/' + l.protocol + '//' + l.hostname + '/pontoon/hooks/php/test/testpilot/');

    // Set include script URL
    $("#install code").html('&lt;script src="' + base + 'static/pontoon.js"&gt;&lt;/script&gt;');





    /*** HOME ***/
    if ($('body').is('.home')) {
      var acceptLanguage = $('#server').data('accept-language');
      if ($('.locale .menu .language.' + acceptLanguage).length === 0) { // Locale not on the list
        acceptLanguage = $('.locale .menu .language').attr('class').split(' ')[1];
      }

      $('.locale .button .language').addClass(acceptLanguage).html($('.locale .menu .language.' + acceptLanguage).html());
      $('#install').css('visibility', 'visible');
      $('#project-load').hide();
      $('#intro').css('display', 'table').hide().fadeIn(function() {});



    /*** TRANSLATE ***/
    } else if ($('body').is('.translate')) {
      var url = $('#server').data('url'),
          locale = $('#server').data('locale'),
          escapedLocale = locale.replace(".", "\\.").replace("@", "\\@");

      // Initialize Pontoon only if project code supports it
      function receiveMessage(e) {
        // TODO: Check origin - hardcode Pontoon domain name
        if (JSON.parse(e.data).type === "SUPPORTED") {
          $('#main').slideDown(function() {
            $('#source').show().height($(document).height() - $(this).height());
            $('#project-load').hide();
          });
          Pontoon.init(window, $('#source').get(0).contentWindow, locale);
          window.removeEventListener("message", receiveMessage, false);
        }
      }
      window.addEventListener("message", receiveMessage, false);

      $('.url').val(url);
      $('.locale .button .language').addClass(escapedLocale).html($('.locale .menu .language.' + escapedLocale).html());
      $('#source').attr('src', url);

      // Show error message if no callback for 5 seconds: Pontoon/iframe not supported, 404…
      var i = 0,
          interval = setInterval(function() {
            if (i < 50) {
              i++;
              if (Pontoon.app) { // Set in Pontoon.init() which is called on "supported"
                clearInterval(interval);
              }
            } else {
              clearInterval(interval);
              window.location = '/?error=Oops, website is not supported by Pontoon.';
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
        if (e.data.initial.below.height() === 0) {
          $('#main').removeClass('opened');
          Pontoon.common.postMessage("MODE", "Advanced");
        } else {
          $('#main').addClass('opened');
          Pontoon.common.postMessage("MODE", "Basic");
        }      
      };
      $('#drag').bind('mousedown', function(e) {
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



    /*** ADMIN */
    } else if ($('body').is('.admin')) {
      // Unhover on add hover
      $('.project .menu .add').hover(function() {
        $('.project .menu ul li').removeClass('hover');
      }, function() {});

      // Edit project if selected from the menu
      $('.project .menu li').live("click.pontoon", function (e) {
        window.location = 'admin/project/' + $(this).find('.project-url').html();
      });

      // Edit or add project if URL typed and Enter pressed
      $('.url').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        var key = e.keyCode || e.which;
        if (key === 13) { // Enter
          window.location = 'admin/project/' + $(this).val();
          return false;
        }
      });



    /*** ADMIN FORM ***/
    } else if ($('body').is('.admin-form')) {
      // Before submitting the form
      $('form').submit(function (e) {
        // Update locales
        var arr = [];
        $("#selected").siblings('ul').find('li:not(".no-match")').each(function() {
          arr.push($(this).data('id'));
        });
        $('#id_locales').val(arr);

        // Append slash to the URL field
        var url = $('#id_url').val();
        if (url.length > 0 && url[url.length-1] !== '/') {
          $('#id_url').val(url + '/');
        }

        // Update form action
        if (!$('form').attr('action').split('project/')[1]) {
          var action = $('form').attr('action');
          $('form').attr('action', action + $('#id_url').val());
        }
      });

      // Submit form with Enter
      $('html').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        if ($('input[type=text]:not(".search, #id_transifex_username, #id_transifex_password"):focus').length > 0) {
          var key = e.keyCode || e.which;
          if (key === 13) { // Enter
            // A short delay to allow digest of autocomplete before submit 
            setTimeout(function() {
              $('form').submit();
            }, 1);
            return false;
          }
        }
      });

      // Choose locales
      $('.locale.select li').live('click.pontoon', function (e) {
        var target = $(this).parents('.locale.select').siblings('.locale.select').find('ul'),
            clone = $(this).remove();
        target.prepend(clone);
      });

      // Choose/remove all locales
      $('.choose-all, .remove-all').live('click.pontoon', function (e) {
        e.preventDefault();
        var ls = $(this).parents('.locale.select'),
            target = ls.siblings('.locale.select').find('ul'),
            items = ls.find('li').remove();
        target.prepend(items);
      });

      // Update from repository
      $('.svn .button:not(".disabled"), .transifex .button:not(".disabled")').unbind('click.pontoon').bind('click.pontoon', function (e) {
        e.preventDefault();
        $(this).addClass('disabled');
        var source = $(this).data('source'),
            img = $(this).find('img');

        function updateIcon(filename) {
          img.attr('src', '/static/img/' + filename);
        }
        updateIcon('loader-light.gif');

        params = {
          pk: $('input[name=pk]').val()
        }
        if (source === 'svn') {
          params.svn = $('input[name=svn]').val();
        } else if (source === 'transifex') {
          $('.transifex input').each(function() {
            var val = $(this).val();
            if (val) {
              if ($(this).attr('name') === 'remember') {
                params[$(this).attr('name')] = ($(this).is(':checked')) ? "on" : "off";
              } else {
                params[$(this).attr('name')] = val;
              }
            }
          });
        }

        $.ajax({
          url: '/admin/' + source + '/',
          data: params,
          success: function(data) {
            if (data === "200") {
              updateIcon('ok.png');
              $('.' + source).removeClass('popup');
            } else if (data === "authenticate") {
              updateIcon('update.png');
              $('.' + source).addClass('popup');
            } else if (data === "error"){
              updateIcon('error.png');
            }
          },
          error: function() {
            updateIcon('error.png');
          }
        }).complete(function() {
          img.parent().removeClass('disabled');
          setTimeout(function() {
            updateIcon('update.png');
          }, 5000);
        });
      });

      // Delete subpage
      $('.delete-subpage').live('click.pontoon', function (e) {
        e.preventDefault();
        $(this).toggleClass('active');
        $(this).next().prop('checked', !$(this).next().prop('checked'));
      });
      $('.subpages [checked]').click().prev().click();

      // Add subpage
      var count = $('.subpages:last').data('count');
      $('.add-subpage').click(function(e) {
        e.preventDefault();
        var form = $('.subpages:last').html().replace(/__prefix__/g, count);
        $(this).before('<div class="subpages clearfix">' + form + '</div>');
        count++;
        $('#id_subpage_set-TOTAL_FORMS').val(count);
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
