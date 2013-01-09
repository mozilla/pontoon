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



    /*** HOME ***/
    if ($('body').is('.home')) {
      // Update URL and project values
      var locale = ($('#server').data('locale') || $('#server').data('accept-language')).toLowerCase();
      if ($('.locale .menu .language.' + locale).length === 0) { // Locale not on the list
        locale = $('.locale .menu .language').attr('class').split(' ')[1];
      }
      $('.url').val($('#server').data('url'));
      $('.locale .button .language').addClass(locale).html($('.locale .menu .language.' + locale).html());

      $('#project-load').hide();
      $('#intro').css('display', 'table').hide().fadeIn();

      // Authentication and profile menu
      $("#browserid").click(function(e) {
        $('#loading').toggleClass('loader').html('&nbsp;');
        e.preventDefault();
        navigator.id.get(function(assertion) {
          if (assertion) {
            $.ajax({
              url: 'browserid/',
              type: 'POST',
              data: {
                assertion: assertion,
                csrfmiddlewaretoken: $('#server').data('csrf')
              },
              success: function(data) {
                $('#action').remove();
                $('#signout').removeClass('hidden').find('a').attr('title', data.browserid.email);
                if (data.manager) {
                  $('#admin').removeClass('hidden');
                }
                if (data.localizer) {
                  $('form').removeClass('hidden');
                  $('.notification').addClass('hidden').removeClass('center');
                } else {
                  $('.notification').html('<li>You don\'t have permission to localize.</li>').removeClass('hidden');
                }
              },
              error: function() {
                $('.notification').html('<li>Oops, something went wrong.</li>').removeClass('hidden');
                $('#loading').toggleClass('loader').html('or');
              }
            });
          } else {
            $('#loading').toggleClass('loader').html('or');
          }
        });
      });



    /*** TRANSLATE ***/
    } else if ($('body').is('.translate')) {
      var url = $('#server').data('url'),
          locale = $('#server').data('locale'),
          escapedLocale = locale.replace(".", "\\.").replace("@", "\\@"),
          projectWindow = null;

      // Initialize Pontoon only if project code supports it
      function receiveMessage(e) {
        // TODO: Check origin - hardcode Pontoon domain name
        if (JSON.parse(e.data).type === "SUPPORTED") {
          $('#main').slideDown(function() {
            $('#source').show().height($(document).height() - $(this).height());
            $('#project-load').hide();
          });
          Pontoon.init(window, projectWindow, locale);
          window.removeEventListener("message", receiveMessage, false);
        }
      }
      window.addEventListener("message", receiveMessage, false);

      $('.url').val(url);
      $('.locale .button .language').addClass(escapedLocale).html($('.locale .menu .language.' + escapedLocale).html());
      if ($('#server').data('external') !== true) {
        $('#source').attr('src', url);
        projectWindow = $('#source')[0].contentWindow;
      } else {
        $('#switch, #drag').remove();
        $('#main').prepend($('#entitylist').remove()).toggleClass('opened');
        $(window).resize(function () {
          $('#entitylist').height($(document).height() - $('#main > header').outerHeight());
        });
        $("#entitylist").height($(document).height() - $('#main > header').outerHeight());
        projectWindow = window.open(url, 'project', 'width=320,height=480,toolbar=1,resizable=1,scrollbars=1');
      }

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
              if (projectWindow) {
                window.location = errorLink + '&error=' + "Oops, website is not supported by Pontoon.";
                projectWindow.close();
              } else {
                window.location = errorLink + '&error=' + 'Oops, looks like pop-ups are blocked.';
              }
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
              max: $(document).height() - $("#main header").outerHeight()
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
        e.preventDefault();
        $('.url').val($(this).find('.project-name').html());
        window.location = 'admin/project/' + $(this).find('.project-name').html();
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
        $('form').attr('action', $('form').attr('action').split('/project/')[0] + '/project/' + $('#id_name').val() + '/');
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
            items = ls.find('li:visible:not(".no-match")').remove();
        target.prepend(items);
      });

      // Update from repository
      $('.repository .button:not(".disabled"), .transifex .button:not(".disabled")').unbind('click.pontoon').bind('click.pontoon', function (e) {
        e.preventDefault();
        $(this).addClass('disabled');
        var source = $(this).data('source'),
            img = $(this).find('img');

        function updateIcon(filename) {
          img.attr('src', '/static/img/' + filename);
        }
        updateIcon('loader-light.gif');

        params = {
          pk: $('input[name=pk]').val(),
          csrfmiddlewaretoken: $('#server').data('csrf')
        }
        if (source === 'repository') {
          params.repository = $('input[name=repository]').val();
        } else if (source === 'transifex') {
          if ($(this).parents('.popup').length === 0) {
            project = $('.transifex input#id_transifex_project');
            resource = $('.transifex input#id_transifex_resource');
            params[project.attr('name')] = project.val();
            params[resource.attr('name')] = resource.val();
          } else {
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
        }

        $.ajax({
          url: '/admin/' + source + '/',
          type: 'POST',
          data: params,
          success: function(data) {
            if (data === "200") {
              updateIcon('ok.png');
              $('.' + source).removeClass('popup');
              $('.warning').fadeOut();
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

      // Delete project
      $('.delete-project').live('click.pontoon', function (e) {
        e.preventDefault();
        if ($(this).is('.clicked')) {
          window.location = '/admin/delete/' + $('input[name=pk]').val();
        } else {
          $(this).addClass('clicked').html('Are you sure?');
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
