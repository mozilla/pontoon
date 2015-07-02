/* Public functions used across different files */
var Pontoon = (function (my) {
  return $.extend(true, my, {

    /*
     * Get details available for selected project
     */
    getProjectDetails: function() {
      var resources = null;

      $('.project .menu li .name').each(function() {
        if ($('.project .button .title').html() === $(this).html()) {
          resources = $(this).data('details');
          return false;
        }
      });

      return resources;
    },

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
          .removeClass('hide');
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
     * Request new locale for project
     *
     * locale Locale code
     * project Project slug
     */
    requestLocale: function(locale, project) {
      $.ajax({
        url: 'request-locale/',
        type: 'POST',
        data: {
          csrfmiddlewaretoken: $('#server').data('csrf'),
          project: project,
          locale: locale
        },
        success: function(data) {
          if (data !== "error") {
            Pontoon.endLoader(
              'New locale (' + locale + ') requested.', '', true);
          } else {
            Pontoon.endLoader('Oops, something went wrong.', 'error');
          }
        },
        error: function() {
          Pontoon.endLoader('Oops, something went wrong.', 'error');
        },
        complete: function() {
          $('.locale .menu .search-wrapper > a').click();
        }
      });
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
     * string HTML snippet that has to be displayed as code instead of rendered
     */
    doNotRender: function (string) {
      return string.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },


    /*
     * Reverse function: do render HTML tags
     *
     * string HTML snippet that has to be rendered instead of displayed as code
     */
    doRender: function (string) {
      return string.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
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
          tab_id = target || 'machinery',
          loader = loader || 'helpers li a[href="#' + tab_id + '"]',
          ul = $('#' + tab_id).find('ul').empty(),
          tab = $('#' + loader).addClass('loading'),
          requests = 0;

      function complete(jqXHR, status) {
        if (status !== "abort") {
          requests--;
          if (requests === 0) {
            tab.removeClass('loading');
            if (ul.find('li').length === 0) {
              ul.append('<li class="disabled">' +
                '<p>No translations available.</p>' +
              '</li>');
            }
          }
        }
      }

      function append(data) {
        ul.append('<li title="Click to copy">' +
          '<header>' +
            '<span class="stress">' + (data.quality || '') +
              (data.count ? ' &bull; <span>#</span>' + data.count : '') +
            '</span>' +
            '<a href="' + data.url + '" target="_blank"' +
              'title="' + data.title + '">' + data.source + '</a>' +
          '</header>' +
          '<p class="original">' + self.doNotRender(data.original || '') + '</p>' +
          '<p class="translation">' + self.doNotRender(data.translation) +
          '</p>' +
        '</li>');

        // Sort by quality
        var listitems = ul.children("li");
        listitems.sort(function(a, b) {
          var valA = parseInt($(a).find('.stress').html().split('%')[0]) || 0,
              valB = parseInt($(b).find('.stress').html().split('%')[0]) || 0;
          return (valA < valB) ? 1 : (valA > valB) ? -1 : 0;
        });
        ul.append(listitems);
      }

      function error(error) {
        if (error.status === 0 && error.statusText !== "abort") {
          // Allows requesting Machinery again
          editor.machinery = null;
          if (ul.find('li').length === 0) {
            self.noConnectionError(ul);
          }
          tab.removeClass('loading');
        }
      }

      // Translation memory
      requests++;

      if (self.XHRtranslationMemory) {
        self.XHRtranslationMemory.abort();
      }

      self.XHRtranslationMemory = $.ajax({
        url: 'translation-memory/',
        data: {
          text: original,
          locale: self.locale.code,
          pk: !target ? $('#editor')[0].entity.pk : ''
        }

      }).success(function(data) {
        if (data.translations) {
          $.each(data.translations, function() {
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
          url: 'machine-translation/',
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
          url: 'microsoft-terminology/',
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
        url: 'amagama/',
        data: {
          text: original,
          locale: self.locale.code
        }

      }).success(function(data) {
        if (data.translations) {
          $.each(data.translations, function() {
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
      $(['aurora', 'gaia', 'mozilla-org']).each(function(i, v) {
        requests++;

        if (self["XHRtransvision" + v]) {
          self["XHRtransvision" + v].abort();
        }

        self["XHRtransvision" + v] = $.ajax({
          url: 'transvision' + '-' + v + '/',
          data: {
            text: encodeURIComponent(original),
            locale: self.locale.code
          }

        }).success(function(data) {
          if (data.translations && !data.translations.error) {
            $.each(data.translations, function() {
              append({
                original: this.source,
                quality: Math.round(this.quality) + '%',
                url: 'http://transvision.mozfr.org/',
                title: 'Visit Transvision',
                source: data.title,
                translation: this.target
              });
            });
          }
        }).error(error).complete(complete);
      });
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
      $('#iframe-cover').hide(); // iframe fix
      $(this).siblings('.menu').show().end()
             .parents('.select').addClass('opened');
      $('#iframe-cover').show(); // iframe fix
      $('body:not(".admin-project") .menu:visible input[type=search]').focus();
    }
  });

  // Menu hover
  $('.menu').on('mouseenter', 'li', function () {
    $('.menu li.hover').removeClass('hover');
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
            '<div class="approved">Approved<span></span></div>' +
            '<div class="translated">Unapproved<span></span></div>' +
            '<div class="fuzzy">Needs work<span></span></div>' +
            '<div class="untranslated">Untranslated<span></span></div>' +
          '</aside>');
      }

      var data = JSON.parse(chart.data('chart').replace(/'/g, "\"")),
          untranslated = data.total - data.approved - data.translated - data.fuzzy,
          rect = chart[0].getBoundingClientRect(),
          height = $('.tooltip').outerHeight() + 15,
          width = ($('.tooltip').outerWidth() - chart.outerWidth()) / 2,
          left = rect.left + window.scrollX - width,
          top = rect.top + window.scrollY - height;

      $('.tooltip')
        .find('.total span').html(data.total).end()
        .find('.approved span').html(data.approved).end()
        .find('.translated span').html(data.translated).end()
        .find('.fuzzy span').html(data.fuzzy).end()
        .find('.untranslated span').html(untranslated).end()
        .css('left', left)
        .css('top', top)
        .show();
    }
  }).on('mouseleave', 'li .chart-wrapper', function () {
    $('.tooltip:visible').remove();
  });

  // Add case insensitive :contains-like selector to jQuery (search)
  $.expr[':'].containsi = function(a, i, m) {
    return (a.textContent || a.innerText || '')
      .toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
  };

  // Menu search
  $('.menu input[type=search]').click(function (e) {
    e.stopPropagation();
  }).keyup(function(e) {
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
    function val(index, el) {
      if (index !== 2) {
        return $(el).find('span:eq(' + index + ')').html();

      } else {
        if (!$(el).find('.chart').length) {
          return 0;
        }
        var chart = $(el).find('.chart').data('chart'),
            data = JSON.parse(chart.replace(/'/g, "\""));
        return data.approved/data.total;
      }
    }

    var index = $(this).index(),
        current = $(this).attr('class'),
        ul = $(this).parents('.sort').next(),
        listitems = ul.children("li:not('.no-match')"),
        dir = (current === 'asc') ? -1 : 1,
        cls = (current === 'asc') ? 'desc' : 'asc';

    $('.menu .sort span').removeClass();
    $(this).addClass(cls);

    listitems.sort(function(a, b) {
      return (val(index, a) < val(index, b)) ? -dir :
        (val(index, a) > val(index, b)) ? dir : 0;
    });

    ul.append(listitems);
  });

  // Toggle quality checks
  $('.quality-checks').click(function() {
    var self = $(this);
    Pontoon.startLoader();

    $.ajax({
      url: 'quality-checks-switch/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: $('#server').data('csrf')
      },
      success: function(data) {
        if (data === 'ok') {
          self.toggleClass('enabled');
          var status = self.is('.enabled') ? 'enabled' : 'disabled';
          Pontoon.endLoader('Quality checks ' + status + '.');
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
  });

});
