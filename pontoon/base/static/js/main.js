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
     * Close notification
     */
    closeNotification: function () {
      $('.notification').animate({opacity: 0}, function() {
        $(this).addClass('hide');
      });
    },

    /*
     * Display loader to provide feedback about the background process
     */
    startLoader: function () {
      $('#loading').addClass('loader').show();
    },

    /*
     * Remove loader
     *
     * text End of operation text (e.g. Done!)
     * type Notification type (e.g. error)
     * persist Do not close
     */
    endLoader: function (text, type, persist) {
      $('#loading').removeClass('loader');
      if (text) {
        $('.notification')
          .html('<li class="' + (type || "") + '">' + text + '</li>')
          .css('opacity', 100)
          .removeClass('hide menu-open left');
      }

      if (!persist) {
        if (Pontoon.notificationTimeout) {
          clearTimeout(Pontoon.notificationTimeout);
        }
        Pontoon.notificationTimeout = setTimeout(function() {
          Pontoon.closeNotification();
        }, 2000);
      }
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
      return $('<div/>').text(string).html()
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

      return string
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
        var title = loader !== 'search' ? ' title="Copy Into Translation (Tab)"' : '',
            sources = sourcesMap[data.original + data.translation];

        if (sources) {
          sources.append(
            '<li><a class="translation-source" href="' + data.url + '" target="_blank" title="' + data.title + '">' +
              '<span>' + data.source + '</span>' +
              (data.count ? '<sup>' + data.count  + '</sup>' : '') +
            '</a></li>'
          );

        } else {
          var li = $('<li' + title + '>' +
            '<header>' +
              (data.quality ? '<span class="stress">' + data.quality + '</span>' : '') +
              '<ul class="sources">' +
                '<li data-source="' + data.source + '">' +
                  '<a class="translation-source" href="' + data.url + '" target="_blank" title="' + data.title + '">' +
                    '<span>' + data.source + '</span>' +
                    (data.count ? '<sup>' + data.count + '</sup>' : '') +
                  '</a>' +
                '</li>' +
              '</ul>' +
            '</header>' +
            '<p class="original">' + self.doNotRender(data.original || '') + '</p>' +
            '<p class="translation" dir="auto" lang="' + self.locale.code + '">' +
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
                url: 'http://www.microsoft.com/Language/',
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
                   '&recherche=' + original +
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

  // Show/hide menu on click
  $('.selector').click(function (e) {
    if (!$(this).siblings('.menu').is(':visible')) {
      e.stopPropagation();
      $('body:not(".admin-project") .menu, body:not(".admin-project") .popup').hide();
      $('.select').removeClass('opened');
      $('#iframe-cover:not(".hidden")').hide(); // iframe fix
      $(this).siblings('.menu').show().end()
             .parents('.select').addClass('opened');
      $('#iframe-cover:not(".hidden")').show(); // iframe fix
      $('body:not(".admin-project") .menu:visible input[type=search]').focus().trigger('keyup');
    }
  });

  // Menu hover
  $('.menu').on('mouseenter', 'li, .static-links div', function () {
    $('.menu li.hover, .static-links div').removeClass('hover');
    $(this).toggleClass('hover');
  });

  // Menu chart hover
  $('.menu').on('mouseenter', 'li .chart-wrapper', function () {
    var chart = $(this).find('.chart');

    if (chart.length > 0) {
      if ($('.tooltip').length === 0) {
        $('body').prepend(
          '<aside class="tooltip">' +
            '<div class="total">Total<span></span></div>' +
            '<div class="approved">Translated<span></span></div>' +
            '<div class="translated">Suggested<span></span></div>' +
            '<div class="fuzzy">Fuzzy<span></span></div>' +
            '<div class="untranslated">Missing<span></span></div>' +
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
        .find('.approved span').html(data.approved_strings).end()
        .find('.translated span').html(data.translated_strings).end()
        .find('.fuzzy span').html(data.fuzzy_strings).end()
        .find('.untranslated span').html(untranslated_strings).end()
        .css('left', left)
        .css('top', top)
        .show();
    }
  }).on('mouseleave', 'li .chart-wrapper', function () {
    $('.tooltip:visible').remove();
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

    } else if ($(this).is(".hotkeys")) {
      $('#hotkeys').show();

    } else if ($(this).is('.check-box')) {
      e.stopPropagation();
    }
  });

  // Menu search
  $('.menu input[type=search]').click(function (e) {
    e.stopPropagation();
  }).on('keyup.search', function(e) {
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
  });

  // Menu sort
  $('.menu .sort span').click(function (e) {
    function getChart(el) {
      var data = $(el).find('.chart').data('chart'),
          approved = data ? data.approved_strings/data.total_strings : 0,
          translated = data ? data.translated_strings/data.total_strings : 0;

      return {
        "approved": approved,
        "translated": translated
      };
    }

    function getDate(el) {
      var date = $(el).find('time').attr('datetime') || 0;
      return new Date(date);
    }

    function getString(el) {
      return $(el).find('span:eq(' + index + ')').text();
    }

    var node = $(this),
        index = node.index(),
        ul = node.parents('.sort').next(),
        listitems = ul.children("li:not('.no-match')"),
        dir = node.hasClass('asc') ? -1 : 1,
        cls = node.hasClass('asc') ? 'desc' : 'asc';

    $('.menu .sort span').removeClass('asc desc');
    node.addClass(cls);

    listitems.sort(function(a, b) {
      // Sort by approved, then by unapproved percentage
      if (node.is('.progress')) {
        var chartA = getChart(a),
            chartB = getChart(b);

        return (chartA.approved - chartB.approved) * dir ||
          (chartA.translated - chartB.translated) * dir;

      // Sort by date
      } else if (node.is('.latest')) {
        return (getDate(b) - getDate(a)) * dir;

      // Sort by alphabetical order
      } else {
        return getString(a).localeCompare(getString(b)) * dir;
      }
    });

    ul.append(listitems);
  });

  // Tabs
  $(".tabs nav a").click(function (e) {
    e.preventDefault();
    e.stopPropagation();

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
    Pontoon.startLoader();

    $.ajax({
      url: '/api/v1/user/' + $('#server').data('email') + '/',
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
          $('.notification').addClass('menu-open');

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
      var options = (type === "up") ? ["first", "last", "prevAll"] :
        ["last", "first", "nextAll"];

      if (hovered.length === 0 ||
          menu.find('li:visible:' + options[0]).is('.hover')) {
        menu.find('li.hover').removeClass('hover');
        menu.find('li:visible:' + options[1]).addClass('hover');

      } else {
        menu.find('li.hover').removeClass('hover')
          [options[2]](':visible:not(".horizontal-separator"):first')
            .addClass('hover');
      }

      if (menu.parent().is('.project, .part, .locale')) {
        Pontoon.updateScroll(menu.find('ul'));
      }
    }

    var key = e.which;

    if ($('.menu').is(':visible')) {
      var menu = $('.menu:visible'),
          hovered = menu.find('li.hover');

      // Skip for the tabs
      if (menu.is('.tabs')) {
        return;
      }

      // Up arrow
      if (key === 38) {
        moveMenu("up");
        return false;
      }

      // Down arrow
      if (key === 40) {
        moveMenu("down");
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
        menu.siblings('.selector').click();
        return false;
      }
    }

    // Escape: close
    if ($('.popup').is(':visible') && key === 27) {
      $('body').click();
      return false;
    }

    // Ctrl + Alt + F: focus search
    if ($('#sidebar').is(':visible') && (Pontoon.app.advanced || !$('#editor').is('.opened'))
        && e.ctrlKey && e.altKey && key === 70) {
      $('#search').focus();
      return false;
    }

  });

  var signinSelectors = '#profile .menu li.sign-in, p#sign-in-required > a#sidebar-signin, ul.links > li#sign-in';

  if ($(signinSelectors).length) {
    // Asynchronously load Persona to avoid blocking JS execution
    $.getScript('https://login.persona.org/include.js');

    // Sign in handler
    $('body').on('click', signinSelectors, function (e) {
      e.preventDefault();
      var info = $('#browserid-info').data('info');

      Pontoon.startLoader();

      navigator.id.watch({
        onlogin: function(verifyResult) {
          $.get(info.csrfUrl).then(function(csrfToken) {
            $.ajax({
              url: info.loginUrl,
              type: 'POST',
              data: {
                csrfmiddlewaretoken: csrfToken,
                assertion: verifyResult
              },
              success: function(data) {
                window.location.reload();
              },
              error: function(data) {
                Pontoon.endLoader('Oops, something went wrong.', 'error');
              }
            });
          });
        }
      });

      try {
        navigator.id.request(info.requestArgs);
      }
      catch(ex) { }
    });
  }

});
