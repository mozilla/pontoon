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
      $('.notification').animate({opacity: 0});
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
          .html('<li class="' + type + '">' + text + '</li>')
          .css('opacity', 100);
      }
      if (!persist) {
        setTimeout(function() {
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

  // Show only parts available for the selected project
  $('.part .selector').click(function () {
    var details = Pontoon.getProjectDetails(),
        menu = $(this).siblings('.menu').find('ul'),
        locale = $.trim($('.locale .selector .code').html().toLowerCase());

    if (details) {
      menu.find('li:not(".no-match")').remove();
      $(details[locale]).each(function() {
        if (this.name) {
          var title = this.name,
              percent = '';
        } else {
          var title = this.resource__path,
              share = 0;

          if (this.resource__entity_count > 0) {
            share = (this.approved_count + this.translated_count) /
                    this.resource__entity_count * 100;
          }

          percent = Math.floor(share) + '%';
        }
        menu.append('<li><span>' + title + '</span>' +
          '<span>' + percent + '</span></li>');
      });
    }

    $('.menu:visible input[type=search]').trigger("keyup");
  });

  // Show only locales available for the selected project
  $('.locale .selector').click(function () {
    var details = Pontoon.getProjectDetails(),
        menu = $(this).siblings('.menu');

    $('.locale .search-wrapper > a').removeClass('back').find('span')
      .removeClass('fa-chevron-left').addClass('fa-plus-square');

    menu.find('.limited').removeClass('limited').end().find('li').hide();
    $(Object.keys(details)).each(function() {
      menu.find('.language.' + this).parent().addClass('limited').show();
    });

    $('.menu:visible input[type=search]').trigger("keyup");
  });

  // Open selected project (part) and locale combination
  $('#go').click(function (e) {
    e.preventDefault();
    e.stopPropagation();

    var locale = $('.locale .selector .language').attr('class').split(' ')[1],
        project = $('.project .selector .title').data('slug'),
        part = $('.part .selector:visible').attr('title'),
        loc = locale + '/' + project;

    if (part) {
      loc += '/' + part;
    }
    window.location = loc;
  });

  // Project menu handler
  $('.project .menu li:not(".no-match")').bind('click.main', function () {
    var project = $(this).find('.name'),
        name = project.html(),
        slug = project.data('slug');

    $('.project .selector .title')
      .html(name)
      .data('slug', slug);

    var details = Pontoon.getProjectDetails(),
        locales = Object.keys(details),
        menu = $('.locale .menu'),
        locale = menu.siblings('.selector')
          .find('.code').html().toLowerCase();

    // Fallback if selected locale not available for the selected project
    if (locales.indexOf(locale) === -1) {
      locale = locales[0];

      var accept = $('#server').data('accept-language');
      if (accept) {
        accept = accept.toLowerCase();
        if (locales.indexOf(accept) !== -1) {
          locale = accept;
        }
      }

      menu.find('.language.' + locale).click();
    }

    // Fallback if selected part not available for the selected project
    if (details[locale].length > 0) {
      var detail = details[locale][0],
          isPath = Object.keys(detail).indexOf("name") === -1,
          type = isPath ? 'resource__path' : 'name';
          part = $('.part .selector').attr('title');

      // Selected part available
      for (var d in details[locale]) {
        if (details[locale][d][type] === part) {
          return;
        }
      }

      var defaultPart = detail[type];
      $('header .part').removeClass("hidden")
        .find('.selector')
          .attr('title', defaultPart)
          .find('.title')
            .html(defaultPart.replace(/^.*[\\\/]/, ''));
    } else {
      $('header .part').addClass("hidden");
    }
  });

  // Parts menu handler
  $('.part .menu').on('click.pontoon', 'li:not(".no-match")', function () {
    var title = $(this).find('span:first').html();
    $('.part .selector')
      .attr('title', title)
      .find('.title')
        .html(title.replace(/^.*[\\\/]/, ''));
  });

  // Locale menu handler
  $('.locale .menu li:not(".no-match")').bind("click.main", function () {
    var locale = $(this).find('.language').attr('class').split(' ')[1],
        // Escape special characters in CSS notation
        code = locale.replace( /(:|\.|\[|@|\])/g, "\\$1" ),
        language = $('.locale .menu .language.' + code).parent().html();

    // Request new locale
    if ($('.locale .menu .search-wrapper > a').is('.back')) {
      var project = $('.project .title').data('slug');
      Pontoon.requestLocale(locale, project);

    // Select locale
    } else {
      $('.locale .selector').html(language);
    }
  });

  // Switch between available locales and locales to request
  $('.locale .menu .search-wrapper > a').bind("click.main", function (e) {
    e.stopPropagation();
    e.preventDefault();

    $(this).toggleClass('back')
      .find('span').toggleClass('fa-plus-square fa-chevron-left');

    if ($(this).is('.back')) {
      var details = Pontoon.getProjectDetails(),
          menu = $(this).parents('.menu');

      menu.find('li').addClass('limited').show();
      $(Object.keys(details)).each(function() {
        menu.find('.language.' + this).parent()
          .removeClass('limited').hide();
      });
      $('.menu:visible input[type=search]').trigger("keyup").focus();

    } else {
      $('.locale .selector').click().click();
    }
  });

  // Add case insensitive :contains-like selector to jQuery (search)
  $.expr[':'].containsi = function(a, i, m) {
    return (a.textContent || a.innerText || '')
      .toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
  };

  // Project, part and locale search
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

  // Update progress popup
  $('#progress .selector').click(function() {
    if (!$(this).find('.menu').is(':visible')) {
      $('#progress .menu .big')
        .empty()
        .append($('#progress .selector').html());
    }
  });

  // General keyboard shortcuts
  $('html').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
    var key = e.which;

    if ($('.menu').is(':visible')) {
      var menu = $('.menu:visible'),
          hovered = menu.find('li.hover');

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

    if ($('.popup').is(':visible')) {
      var popup = $('.popup:visible');

      // Enter: confirm
      if (key === 13) {
        popup.find('.button').click();
        return false;
      }

      // Escape: close
      if (key === 27) {
        popup.find('.cancel').click();
        return false;
      }
    }

    if ($('#sidebar').is(':visible')) {

      // Alt + F: focus search
      if (Pontoon.app.advanced || !$("#editor").is('.opened')) {
        if (e.altKey && key === 70) {
          $('#search').focus();
          return false;
        }
      }

      // Tab: select suggestions
      if (!$('.menu').is(':visible') && !$('.popup').is(':visible') &&
          (Pontoon.app.advanced || $("#editor").is('.opened')) &&
          !$('#custom-search').is(':visible')) {
        if (key === 9) {
          var section = $('#helpers section:visible'),
              index = section.find('li.hover').index() + 1;

          // If possible, select next suggestion, or select first
          if (section.find('li:last').is('.hover')) {
            index = 0;
          }

          section
            .find('li').removeClass('hover').end()
            .find('li:eq(' + index + ')').addClass('hover').click();

          Pontoon.updateScroll(section);
          return false;
        }
      }
    }
  });

});

