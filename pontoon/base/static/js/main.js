/* Must be available immediately */
// Add case insensitive :contains-like selector to jQuery (search)
$.expr[':'].containsi = function(a, i, m) {
  return (a.textContent || a.innerText || '')
    .toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
};



/* Public functions used across different files */
var Pontoon = (function (my) {
  return $.extend(true, my, {

    /*
     * Bind NProgress (slim progress bar on top of the page) to each AJAX request
     */
    NProgressBind: function () {
      NProgress.configure({ showSpinner: false });
      $(document).bind('ajaxStart.nprogress', function() {
        NProgress.start();
      }).bind('ajaxStop.nprogress', function() {
        NProgress.done();
      });
    },

    /*
     * Unbind NProgress
     */
    NProgressUnbind: function () {
      $(document).unbind('.nprogress');
    },

    /*
     * Mark all notifications as read and update UI accordingly
     */
    markAllNotificationsAsRead: function () {
      this.NProgressUnbind();

      $.ajax({
        url: '/notifications/mark-all-as-read/',
        success: function() {
          $('#notifications.unread .button .icon').animate({color: '#4D5967'}, 1000);
          var unreadNotifications = $('#main.notifications .right-column li.notification-item[data-unread="true"]');

          unreadNotifications.animate({backgroundColor: 'transparent'}, 1000, function() {
            // Remove inline style and unread mark to make hover work again
            unreadNotifications.removeAttr('style').removeAttr('data-unread');
          });
        }
      });

      this.NProgressBind();
    },

    /*
     * Close notification
     */
    closeNotification: function () {
      $('.notification').animate({
        bottom: '-60px',
      }, {
        duration: 200
      }, function() {
        $(this).addClass('hide').empty();
      });
    },

    /*
     * Remove loader
     *
     * text End of operation text (e.g. Done!)
     * type Notification type (e.g. error)
     * duration How long should the notification remain open (default: 2000 ms)
     */
    endLoader: function (text, type, duration) {
      if (text) {
        $('.notification')
          .html('<li class="' + (type || '') + '">' + text + '</li>')
          .removeClass('hide')
          .animate({
            bottom: 0,
          }, {
            duration: 200
          });
      }

      if (Pontoon.notificationTimeout) {
        clearTimeout(Pontoon.notificationTimeout);
      }
      Pontoon.notificationTimeout = setTimeout(function() {
        Pontoon.closeNotification();
      }, duration || 2000);
    },

    /*
     * Update scrollbar position in the menu
     *
     * menu Menu element
     */
    updateScroll: function (menu) {
      var hovered = menu.find('[class*=hover]'),
          maxHeight = menu.height(),
          visibleTop = menu.scrollTop(),
          visibleBottom = visibleTop + maxHeight,
          hoveredTop = visibleTop + hovered.position().top,
          hoveredBottom = hoveredTop + hovered.outerHeight();

      if (hoveredBottom >= visibleBottom) {
        menu.scrollTop(Math.max(hoveredBottom - maxHeight, 0));
      } else if (hoveredTop < visibleTop) {
        menu.scrollTop(hoveredTop);
      }
    },

    /*
     * Do not render HTML tags
     *
     * string String that has to be displayed as is instead of rendered
     */
    doNotRender: function (string) {
      return $('<div/>').text(string).html();
    },

    /*
     * Strip HTML tags from the given string
     */
    stripHTML: function (string) {
      return $($.parseHTML(string)).text();
    },

    /*
     * Converts a number to a string containing commas every three digits
     */
    numberWithCommas: function (number) {
      return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    /*
     * Markup placeables
     */
    markPlaceables: function (string) {
      function getReplacement(title, replacement) {
        return '<mark class="placeable" title="' + title + '">' + replacement + '</mark>';
      }

      function markup(string, regex, title, replacement) {
        replacement = replacement || '$&';
        return string.replace(regex, getReplacement(title, replacement));
      }

      string = this.doNotRender(string);

      /* Special spaces */
      // Pontoon.doNotRender() replaces \u00A0 with &nbsp;
      string = markup(string, /&nbsp;/gi, 'Non-breaking space');
      string = markup(string, /[\u202F]/gi, 'Narrow non-breaking space');
      string = markup(string, /[\u2009]/gi, 'Thin space');

      /* Multiple spaces */
      string = string.replace(/  +/gi, function(match) {
        var title = 'Multiple spaces',
            replacement = '';

        for (var i=0; i<match.length; i++) {
          replacement += ' &middot; ';
        }

        return getReplacement(title, replacement);
      });

      /* Leading and Trailing spaces */
      string = markup(string, /^ /gi, 'Leading space');
      string = markup(string, / $/gi, 'Trailing space');

      /* Tab */
      string = markup(string, /\t/gi, 'Tab character', '&rarr;');

      /* Newline */
      string = markup(string, /\n/gi, 'Newline character', '¶$&');

      return string;
    },

    /*
     * Mark diff between the string and the reference string
     */
    diff: function (reference, string) {
      var self = this,
          diff_obj = new diff_match_patch(),
          diff = diff_obj.diff_main(reference, string),
          output = '';
      diff_obj.diff_cleanupSemantic(diff);
      diff_obj.diff_cleanupEfficiency(diff);

      $.each(diff, function() {
        var type = this[0],
            slice = this[1];

        // Inserted
        if (type === 1) {
          output += '<ins>' + self.markPlaceables(slice) + '</ins>';
        }

        // Deleted
        if (type === -1) {
          output += '<del>' + self.markPlaceables(slice) + '</del>';
        }

        // Equal
        if (type === 0) {
          output += self.markPlaceables(slice);
        }
      });

      return output;
    },

    /*
     * Linkifies any traces of URLs present in a given string.
     *
     * Matches the URL Regex and parses the required matches.
     * Can find more than one URL in the given string.
     */
    linkify: function (string) {
      // http://, https://, ftp://
      var urlPattern = /\b(?:https?|ftp):\/\/[a-z0-9-+&@#\/%?=~_|!:,.;]*[a-z0-9-+&@#\/%=~_|]/gim;
      // www. sans http:// or https://
      var pseudoUrlPattern = /(^|[^\/])(www\.[\S]+(\b|$))/gim;

      return this.doNotRender(string)
        .replace(urlPattern, '<a href="$&" target="_blank">$&</a>')
        .replace(pseudoUrlPattern, '$1<a href="http://$2" target="_blank">$2</a>');
    },

    /*
     * Show no connection error in helpers
     *
     * list List to append no connection error to
     */
    noConnectionError: function (list) {
      list.append(
        '<li class="disabled">' +
          '<p>Content not available while offline.</p>' +
          '<p>Check your connection and try again.</p>' +
        '</li>');
    },

    /*
     * Get suggestions from machine translation and translation memory
     *
     * original Original string
     * target Target element id
     * loader Loader element id
     */
    getMachinery: function (original, target, loader) {
      var self = this,
          loader = loader || 'helpers li a[href="#machinery"]',
          ul = $('#helpers > .machinery').children('ul').empty(),
          tab = $('#' + loader).addClass('loading'),
          requests = 0,
          count = 0,
          sourcesMap = {};

      function append(data) {
        var title = loader !== 'search' ? ' title="Copy Into Translation (Tab)"' : ' title="Copy to clipboard"',
            sources = sourcesMap[data.original + data.translation],
            occurrencesTitle = 'Number of translation occurrences';

        if (sources) {
          sources.append(
            '<li><a class="translation-source" href="' + data.url + '" target="_blank" title="' + data.title + '">' +
              '<span>' + data.source + '</span>' +
              (data.count ? '<sup title="' + occurrencesTitle + '">' + data.count  + '</sup>' : '') +
            '</a></li>'
          );

        } else {
          var li = $('<li class="suggestion"' + title + ' data-clipboard-text="' + self.doNotRender(data.translation) + '">' +
            '<header>' +
              (data.quality ? '<span class="stress">' + data.quality + '</span>' : '') +
              '<ul class="sources">' +
                '<li data-source="' + data.source + '">' +
                  '<a class="translation-source" href="' + data.url + '" target="_blank" title="' + data.title + '">' +
                    '<span>' + data.source + '</span>' +
                    (data.count ? '<sup title="' + occurrencesTitle + '">' + data.count + '</sup>' : '') +
                  '</a>' +
                '</li>' +
              '</ul>' +
            '</header>' +
            '<p class="original">' + (data.original ? self.diff(original, data.original) : '') + '</p>' +
            '<p class="translation" dir="' + self.locale.direction + '" lang="' + self.locale.code + '" data-script="' + self.locale.script + '">' +
              self.markPlaceables(data.translation) +
            '</p>' +
            '<p class="translation-clipboard">' +
              self.doNotRender(data.translation) +
            '</p>' +
          '</li>');
          ul.append(li);
          sourcesMap[data.original + data.translation] = li.find('.sources');
          count++;
        }

        // Sort by quality
        var listitems = ul.children("li"),
            sourceMap = {
              'Translation memory': 1,
              'Mozilla': 2,
              'Open Source': 3,
              'Microsoft': 4,
              'Machine Translation': 5
            };

        function getTranslationSource(el) {
          var sources = $(el).find('.translation-source span');

          if (sources.length > 1) {
            return Math.min.apply(Math, $.map(sources, function(elem) {
              return sourceMap[$(elem).text()];
            }));
          } else {
            return sourceMap[sources.text()];
          }
        }

        listitems.sort(function(a, b) {
          var stressA = $(a).find('.stress'),
              stressB = $(b).find('.stress'),
              valA = stressA.length ? parseInt(stressA.html().split('%')[0]) : 0,
              valB = stressB.length ? parseInt(stressB.html().split('%')[0]) : 0,
              sourceA = getTranslationSource(a),
              sourceB = getTranslationSource(b);

          return (valA < valB) ? 1 : (valA > valB) ? -1 : (sourceA > sourceB) ? 1 : (sourceA < sourceB) ? -1 : 0;
        });

        ul.html(listitems);

        // Sort sources inside results.
        ul.find('.sources').each(function (index) {
          var $sourcesList = $(this),
              sources = $sourcesList.children('li'),
              sortedItems = sources.sort(function(a, b) {
                var sourceA = sourceMap[$(a).find('span').text()],
                    sourceB = sourceMap[$(b).find('span').text()];
                return (sourceA > sourceB) ? 1 : (sourceA < sourceB) ? -1 : 0;
              });

          $sourcesList.children('li').remove();

          sortedItems.each(function() {
            $sourcesList.append(this);
          });
        });
      }

      function error(error) {
        if (error.status === 0 && error.statusText !== "abort") {
          // Allows requesting Machinery again
          editor.machinery = null;
          if (ul.children('li').length === 0) {
            self.noConnectionError(ul);
          }
        }
      }

      function complete(jqXHR, status) {
        if (status !== "abort") {
          requests--;
          tab.find('.count').html(count).toggle(count !== 0);
          if (requests === 0) {
            tab.removeClass('loading');
            if (ul.children('li').length === 0) {
              ul.append('<li class="disabled">' +
                '<p>No translations available.</p>' +
              '</li>');
            }
          }
        }
      }

      // Reset count
      tab.find('.count').html('').hide();

      // Translation memory
      requests++;

      if (self.XHRtranslationMemory) {
        self.XHRtranslationMemory.abort();
      }

      self.XHRtranslationMemory = $.ajax({
        url: '/translation-memory/',
        data: {
          text: original,
          locale: self.locale.code,
          pk: !target ? $('#editor')[0].entity.pk : ''
        }

      }).success(function(data) {
        if (data) {
          $.each(data, function() {
            append({
              original: this.source,
              quality: Math.round(this.quality) + '%',
              url: '/',
              title: 'Pontoon Homepage',
              source: 'Translation memory',
              translation: this.target,
              count: this.count
            });
          });
        }
      }).error(error).complete(complete);

      // Machine translation
      if (self.locale.mt !== false) {
        requests++;

        if (self.XHRmachineTranslation) {
          self.XHRmachineTranslation.abort();
        }

        self.XHRmachineTranslation = $.ajax({
          url: '/machine-translation/',
          data: {
            text: original,
            // On first run, check if target locale supported
            check: (self.locale.mt === undefined) ? true : false,
            // Use MT locale, Pontoon's might not be supported
            locale: (self.locale.mt === undefined) ?
                    self.locale.code : self.locale.mt
          }

        }).success(function(data) {
          if (data.locale) {
            self.locale.mt = data.locale;
          }
          if (data.translation) {
            append({
              url: 'http://www.bing.com/translator',
              title: 'Visit Bing Translator',
              source: 'Machine Translation',
              translation: data.translation
            });
          } else if (data === "not-supported") {
            self.locale.mt = false;
          }
        }).error(error).complete(complete);
      }

      // Microsoft Terminology
      if (self.locale.msTerminology !== false) {
        requests++;

        if (self.XHRmicrosoftTerminology) {
          self.XHRmicrosoftTerminology.abort();
        }

        self.XHRmicrosoftTerminology = $.ajax({
          url: '/microsoft-terminology/',
          data: {
            text: original,
            // On first run, check if target locale supported
            check: (self.locale.msTerminology === undefined) ? true : false,
            // Use Microsoft Terminology locale, Pontoon's might not be supported
            locale: (self.locale.msTerminology === undefined) ?
                    self.locale.code : self.locale.msTerminology
          }

        }).success(function(data) {
          if (data.locale) {
            self.locale.msTerminology = data.locale;
          }
          if (data.translations) {
            $.each(data.translations, function() {
              append({
                original: this.source,
                quality: Math.round(this.quality) + '%',
                url: 'https://www.microsoft.com/Language/en-US/Search.aspx?sString=' + this.source + '&langID=' + self.locale.msTerminology,
                title: 'Visit Microsoft Terminology Service API.\n' +
                       '© 2014 Microsoft Corporation. All rights reserved.',
                source: 'Microsoft',
                translation: this.target
              });
            });
          } else if (data === "not-supported") {
            self.locale.msTerminology = false;
          }
        }).error(error).complete(complete);
      }

      // amaGama
      requests++;

      if (self.XHRamagama) {
        self.XHRamagama.abort();
      }

      self.XHRamagama = $.ajax({
        url: '/amagama/',
        data: {
          text: original,
          locale: self.locale.code
        }

      }).success(function(data) {
        if (data) {
          $.each(data, function() {
            append({
              original: this.source,
              quality: Math.round(this.quality) + '%',
              url: 'http://amagama.translatehouse.org/',
              title: 'Visit amaGama',
              source: 'Open Source',
              translation: this.target
            });
          });
        }
      }).error(error).complete(complete);

      // Transvision
      requests++;

      if (self.XHRtransvision) {
        self.XHRtransvision.abort();
      }

      self.XHRtransvision = $.ajax({
        url: '/transvision/',
        data: {
          text: original,
          locale: self.locale.code
        }

      }).success(function(data) {
        if (data) {
          $.each(data, function() {
            append({
              original: this.source,
              quality: Math.round(this.quality) + '%',
              url: 'https://transvision.mozfr.org/?repo=global' +
                   '&recherche=' + encodeURIComponent(original) +
                   '&locale=' + self.locale.code,
              title: 'Visit Transvision',
              source: 'Mozilla',
              translation: this.target
            });
          });
        }
      }).error(error).complete(complete);
    }

  });
}(Pontoon || {}));



/* Main code */
$(function() {
  Pontoon.NProgressBind();

  // Display any notifications
  var notifications = $('.notification li');
  if (notifications.length) {
    Pontoon.endLoader(notifications.text());
  }

  function getRedirectUrl() {
    return window.location.pathname + window.location.search;
  }

  // Sign in button action
  $('#fxa-sign-in, #standalone-signin a, #sidebar-signin').on('click', function(ev) {
    var $this = $(this);
    var loginUrl = $this.prop('href'),
        startSign = loginUrl.match(/\?/) ? '&': '?';
    $this.prop('href', loginUrl + startSign + 'next=' + getRedirectUrl());
  });

  // Sign out button action
  $('.sign-out a, #sign-out a').on('click', function(ev) {
    var $this = $(this),
        $form = $this.find('form');

    ev.preventDefault();
    $form.prop('action', $this.prop('href') + '?next=' + getRedirectUrl());
    $form.submit();
  });

  // Show/hide menu on click
  $('body').on('click', '.selector', function (e) {
    if (!$(this).siblings('.menu').is(':visible')) {
      e.stopPropagation();
      $('.menu:not(".permanent")').hide();
      $('.select').removeClass('opened');
      $('#iframe-cover:not(".hidden")').hide(); // iframe fix
      $(this).siblings('.menu').show().end()
             .parents('.select').addClass('opened');
      $('#iframe-cover:not(".hidden")').show(); // iframe fix
      $('.menu:not(".permanent"):visible input[type=search]').focus().trigger('input');
    }
  });

  // Hide menus on click outside
  $('body').bind('click.main', function (e) {
    $('.menu:not(".permanent")').hide();
    $('.select').removeClass('opened');
    $('.menu:not(".permanent") li').removeClass('hover');
  });

  // Menu hover
  $('body').on('mouseenter', '.menu li, .menu .static-links div', function () {
    // Ignore on nested menus
    if ($(this).parents('li').length) {
      return false;
    }

    $('.menu li.hover, .static-links div').removeClass('hover');
    $(this).toggleClass('hover');

  }).on('mouseleave', '.menu li, .menu .static-links div', function () {
    // Ignore on nested menus
    if ($(this).parents('li').length) {
      return false;
    }

    $('.menu li.hover, .static-links div').removeClass('hover');
  });

  // Menu chart hover
  $('.menu').on('mouseenter', 'li .chart-wrapper', function () {
    var chart = $(this).find('.chart');

    if (chart.length > 0) {
      if ($('.tooltip').length === 0) {
        $('body').prepend(
          '<aside class="tooltip">' +
            '<div class="total">Total<span></span></div>' +
            '<div class="translated">Translated<span></span></div>' +
            '<div class="suggested">Suggested<span></span></div>' +
            '<div class="fuzzy">Fuzzy<span></span></div>' +
            '<div class="missing">Missing<span></span></div>' +
          '</aside>');
      }

      var data = chart.data('chart'),
          untranslated_strings = data.total_strings - data.approved_strings - data.translated_strings - data.fuzzy_strings,
          rect = chart[0].getBoundingClientRect(),
          height = $('.tooltip').outerHeight() + 15,
          width = ($('.tooltip').outerWidth() - $(this).outerWidth()) / 2,
          left = rect.left + window.scrollX - width,
          top = rect.top + window.scrollY - height;

      $('.tooltip')
        .find('.total span').html(data.total_strings).end()
        .find('.translated span').html(data.approved_strings).end()
        .find('.suggested span').html(data.translated_strings).end()
        .find('.fuzzy span').html(data.fuzzy_strings).end()
        .find('.missing span').html(untranslated_strings).end()
        .css('left', left)
        .css('top', top)
        .show();
    }
  }).on('mouseleave', 'li .chart-wrapper', function () {
    $('.tooltip:visible').remove();
  });

  // Mark notifications as read when notification menu opens
  $('#notifications.unread .button .icon').click(function() {
    Pontoon.markAllNotificationsAsRead();
  });

  // Profile menu
  $('#profile .menu li').click(function (e) {
    if ($(this).has('a').length) {
      return;
    }
    e.preventDefault();

    if ($(this).is('.download')) {
      Pontoon.updateFormFields($('form#download-file'));
      $('form#download-file').submit();

    } else if ($(this).is(".upload")) {
      $('#id_uploadfile').click();

    } else if ($(this).is('.check-box')) {
      e.stopPropagation();
    }
  });

  // Menu search
  $('body').on('click', '.menu input[type=search]', function(e) {
    e.stopPropagation();
  }).on('input.search', '.menu input[type=search]', function(e) {
    // Tab
    if (e.which === 9) {
      return;
    }

    var ul = $(this).parent().siblings('ul'),
        val = $(this).val(),
        // Only search a limited set if defined
        limited = ul.find('li.limited').length > 0 ? '.limited' : '';

    ul
      .find('li' + limited).show().end()
      .find('li' + limited + ':not(":containsi(\'' + val + '\')")').hide();

    if (ul.find('li:not(".no-match"):visible').length === 0) {
      ul.find('.no-match').show();
    } else {
      ul.find('.no-match').hide();
    }
  }).on('keydown.search', '.menu input[type=search]', function(e) {
    // Prevent form submission on Enter
    if (e.which === 13) {
      return false;
    }
  });

  // Tabs
  $('.tabs nav a').click(function (e) {
    e.preventDefault();

    var tab = $(this),
        section = tab.attr('href').substr(1);

    tab
      .parents("li")
        .siblings().removeClass('active').end()
        .addClass('active').end()

      .parents(".tabs")
        .find('section').hide().end()
        .find('section.' + section).show();
  });

  // Toggle user profile attribute
  $('.check-box').click(function() {
    var self = $(this);

    $.ajax({
      url: '/api/v1/user/' + $('#server').data('username') + '/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('#server').data('csrf'),
        attribute: self.data('attribute'),
        value: !self.is('.enabled')
      },
      success: function(data) {
        if (data === 'ok') {
          self.toggleClass('enabled');
          var is_enabled = self.is('.enabled'),
              status = is_enabled ? 'enabled' : 'disabled';

          Pontoon.endLoader(self.text() + ' ' + status + '.');

          if (self.is('.force-suggestions') && Pontoon.user) {
            Pontoon.user.forceSuggestions = is_enabled;
            Pontoon.postMessage("UPDATE-ATTRIBUTE", {
              object: 'user',
              attribute: 'forceSuggestions',
              value: is_enabled
            });
            $('[id^="save"]').toggleClass('suggest', is_enabled);
          }
        }
      },
      error: function() {
        Pontoon.endLoader('Oops, something went wrong.', 'error');
      }
    });
  });

  // General keyboard shortcuts
  $('html').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
    function moveMenu(type) {
      var options = (type === "up") ? ["first", "last", -1] :
        ["last", "first", 1],
          items = menu.find('li:visible:not(.horizontal-separator, .time-range-toolbar, :has(li))');

      if (hovered.length === 0 ||
          menu.find('li:not(:has(li)):visible:' + options[0]).is('.hover')) {
        menu.find('li.hover').removeClass('hover');
        items[options[1]]().addClass('hover');

      } else {
        var current = menu.find('li.hover'),
            next = items.index(current) + options[2];

        current.removeClass('hover');
        $(items.get(next)).addClass('hover');
      }

      if (menu.parent().is('.project, .part, .locale')) {
        Pontoon.updateScroll(menu.find('ul'));
      }
    }

    var key = e.which;

    if ($('.menu:not(".permanent")').is(':visible')) {
      var menu = $('.menu:visible'),
          hovered = menu.find('li.hover');

      // Skip for the tabs
      if (menu.is('.tabs')) {
        return;
      }

      // Up arrow
      if (key === 38) {
        moveMenu('up');
        return false;
      }

      // Down arrow
      if (key === 40) {
        moveMenu('down');
        return false;
      }

      // Enter: confirm
      if (key === 13) {
        var a = hovered.find('a');
        if (a.length > 0) {
          a.click();
        } else {
          hovered.click();
        }
        return false;
      }

      // Escape: close
      if (key === 27) {
        $('body').click();
        return false;
      }
    }

    if ($('#sidebar').is(':visible') && (Pontoon.app.advanced || !$('#editor').is('.opened'))) {
      // Ctrl + Shift + F: Focus Search
      if (e.ctrlKey && e.shiftKey && key === 70) {
        $('#search').focus();
        return false;
      }

      // Ctrl + Shift + A: Select All Strings
      if (Pontoon.user.canTranslate() && e.ctrlKey && e.shiftKey && key === 65) {
        Pontoon.selectAllEntities();
        return false;
      }

      // Escape: Deselect entities and switch to first entity
      if (Pontoon.user.canTranslate() && $('#entitylist .entity.selected').length && key === 27) {
        if (Pontoon.app.advanced) {
          Pontoon.openFirstEntity();
        } else {
          Pontoon.goBackToEntityList();
        }
        return false;
      }
    }
  });
});
