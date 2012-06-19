var Pontoon = (function () {

  'use strict';

  /* public  */
  return {



    /*
     * Save data in different formats
     *
     * type Data format
     * value Data
     */
    save: function (type, value) {
      var self = this,
          params = {
            type: type,
            locale: this.locale.code
          };

      if (type === "html") {
        params.data = value;
        self.confirmLeaving(false);
        window.location = 'download/?' + $.param(params);
        self.confirmLeaving(true);

      } else if (type === "json") {
        var pages = $.extend(true, {}, this.project.pages); // Deep copy: http://api.jquery.com/jQuery.extend
        $(pages[self.project.page].entities).each(function () {
          delete this.ui;
          delete this.hover;
          delete this.unhover;
          delete this.id;
          delete this.body;
        });
        params.data = JSON.stringify(pages, null, "\t");
        self.confirmLeaving(false);
        window.location = 'download/?' + $.param(params);
        self.confirmLeaving(true);

      } else if (type === "po") {
        var po = {
            metadata: {
                'project_title': self.project_title,
                'locale_language': self.locale.language,
                'username': self.user.name,
                'user_email': self.user.email
            },
            translations: {}
        }

        $(this.project.pages).each(function () {
          $(this.entities).each(function () {
            var msgid = this.original;
            po.translations[msgid] = {
                fuzzy: false,
                msgstr: this.translation,
                occurrence: self.project.url,
            };

            if (this.suggestions && !msgstr) {
              po.translations[msgid].fuzzy = true,
              po.translations[msgid].msgstr = this.suggestions[0].translation;
            }
          });
        });

        params.data = JSON.stringify(po);
        self.confirmLeaving(false);
        window.location = 'download/?' + $.param(params);
        self.confirmLeaving(true);

      } else if (type === "transifex") {
        self.startLoader('Saving...');
        var segments = self.transifex.po.split("\n\n"),
            head = segments[0],
            strings = segments.slice(1),
            entities = self.project.pages[self.project.page].entities;

        $(strings).each(function(i, v) {
          var split = v.split("\nmsgstr");
          strings[i] = split[0] + "\nmsgstr \"" + entities[i].translation + "\"";
        });

        self.transifex.po = head + "\n\n" + strings.join("\n\n");
        params.transifex = self.transifex;

        if (value) {
          params.auth = {
            username: value[0].value,
            password: value[1].value,
            remember: value[2] ? 1 : 0
          };
        }

        $.ajax({
          url: 'transifex/',
          data: params,
          success: function(data) {
            if (data === "authenticate") {
              self.endLoader('Please sign in to Transifex.', 'error');
              $("#transifex").show();
            } else if (data === "done") {
              self.endLoader('Done!');
              $('#transifex').hide();
            } else if (data === "error") {
              self.endLoader('Oops, something went wrong.', 'error');
              $('#transifex').hide();
            }
          },
          error: function() {
            self.endLoader('Oops, something went wrong.', 'error');
          }
        });
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



    /**
     * Build source - translation pairs
     */
    entityList: function () {
      var self = this,
          list = $(this.app.win.document).find('#entitylist').empty().append('<ul></ul>'),
          localeMenu = $('.locale .menu').eq(0).html();

      // Render
      $(self.project.pages[self.project.page].entities).each(function () {
        var li = $('<li class="entity' + 
          // append classes to translated and head entities
          (this.translation ? ' translated' : '') + 
          (!this.body ? ' head' : '') + '">' + 
        '<div class="source">' + 
          '<ol class="extra">' + 
            '<li class="active original-string" title="Original string"></li>' + 
            '<li class="other-users" title="Suggestions from other users"></li>' + 
            '<li class="other-locales" title="Translations from other locales"></li>' + 
            '<li class="translation-memory" title="Translation memory"></li>' + 
            '<li class="machine-translation" title="Machine translation by Microsoft Translator"></li>' + 
          '</ol>' +
          '<ol class="content">' + 
            '<li class="active original-string">' + 
              '<header>' + 
                (this.comment ? '<span class="comment" title="' + this.comment + '"></span>' : '') + 
                '<h3>Original string</h3>' + 
              '</header>' + 
              '<p class="source-string">' + self.doNotRender(this.original) + '</p>' + 
            '</li>' + 
            '<li class="other-users">' + 
              '<header>' + 
                (this.suggestions && this.suggestions.length > 1 ? '<a href="#prev" class="prev"></a><a href="#next" class="next"></a>' : '') + 
                '<h3>Other users' + 
                (this.suggestions ? ' (<span class="author">' + this.suggestions[0].author + '</span>)' : '') + 
                '</h3>' + 
              '</header>' + 
              (this.suggestions ? '<p data-id="0" class="source-string">' + this.suggestions[0].translation + '</p>' :
               '<p class="no">No suggestions yet</p>') + 
            '</li>' + 
            '<li class="other-locales">' + 
              '<header class="locale select">' + 
                '<h3 class="selector">' + 
                  '<span class="language">Select locale</span>' + 
                  '<span class="handle"> &#9662;</span>' + 
                '</h3>' + 
                '<div class="menu">' + localeMenu + '</div>' + 
              '</header>' + 
              '<p class="no">Get inspiration from other locales</p>' +
            '</li>' + 
            '<li class="translation-memory">' + 
              '<header><h3>Translation memory</h3></header>' + 
              '<p class="loader"></p>' + 
            '</li>' + 
            '<li class="machine-translation">' + 
              '<header><h3>Machine translation</h3></header>' + 
              '<p class="loader"></p>' + 
            '</li>' + 
          '</ol>' +
          '<div class="toolbar">' + 
            '<a href="#copy" class="copy" title="Copy source to translation"></a>' + 
          '</div>' +
        '</div>' +
        '<div class="translation">' + 
          '<div class="translation-wrapper">' +
            '<textarea>' + (this.translation || '') + '</textarea>' + 
            '<div class="toolbar">' + 
              '<a href="#save" class="save" title="Save translation"></a>' + 
              '<a href="#cancel" class="cancel" title="Cancel and revert to original string"></a>' + 
            '</div>' +
          '</div>' +
        '</div></li>', self.app.win);

        li.get(0).entity = this;
        this.ui = li; /* HTML Element representing string in the main UI */

        list.children('ul').append(li);
      });

      // Main entity list handlers
      $("#main .entity:not('.head')").hover(function () {
        self.common.postMessage("HOVER", this.entity.id);
      }, function () {
        self.common.postMessage("UNHOVER", this.entity.id);
      }).click(function () {
        self.common.postMessage("EDIT");
      });

      // Source menu
      $("#main .extra li").click(function (e) {
        e.stopPropagation();
        var t = $(this),
            li = t.parents('.entity');
        t.parents(".extra").find("li").removeClass("active").end()

          .siblings(".toolbar").hide()
          .siblings(".content")
            .find("li.active").removeClass("active").end()
            .find("li." + t.attr("class")).addClass("active");

        t.addClass("active");

        if (li.find(".content > li:visible p.source-string").length > 0) {
          li.find('.toolbar').show();
        }
      });

      // Original string
      $("#main .extra .original-string").click(function () {
        $(this).parents('.entity').find('.toolbar').show();
      });

      // Other users
      $("#main .extra .other-users").click(function () {
        var li = $(this).parents('.entity');

        if (li.get(0).entity.suggestions) {
          li.find('.toolbar').show();
        }
      });

      // Navigate among suggestions from other users
      $("#main .source").find(".prev, .next").click(function (e) {
        e.stopPropagation();
        var li = $(this).parents('.entity'),
            suggestions = li.get(0).entity.suggestions,
            max = suggestions.length,
            ou = li.find(".other-users"),
            string = ou.find(".source-string"),
            id = string.data("id"),
            next = 0,
            cls = $(this).attr("class");

        if (cls === "prev") {
          next = max - 1;
          if (id > 0) {
            next = id - 1;
          }
        } else if (cls === "next") {
          if (id < max - 1) {
            next = id + 1;
          }
        }

        ou.find(".author").html(suggestions[next].author);
        string
          .html(self.doNotRender(suggestions[next].translation))
          .data("id", next);
      });

      // Other locales
      $("#main .source .other-locales .selector").click(function (e) {
        e.stopPropagation();
        $('#main header .container .menu:visible').siblings('.selector').click();
        if ($(this).siblings(".menu").is(":visible")) {
          $("#main .source .other-locales .menu").hide();
        } else {
          $("#main .source .other-locales .menu").hide();
          $(this).siblings('.menu').show();
        }
        // TODO: join with same expression in Pontoon.common() 
        $('.search').val('').focus().siblings('ul').scrollTop(0).find('.no-match').hide().siblings().removeClass('hover').show();
      });
      $("#main .source .other-locales .select .menu li").click(function (e) {
        e.stopPropagation();
        var li = $(this),
            entity = li.parents(".entity"),
            original = entity[0].entity.original,
            locale = li.find(".language").attr("class").split(" ")[1],
            p = li.parents('.select').next('p').show();

        p.addClass("loader").html('');
        li.parents('.menu').siblings('.selector')
          .find('.language').attr('class', li.find('.language').attr('class')).html(li.find('.language').contents()[0].nodeValue).end().end()
        .hide();

        // TODO: AJAX request to display only locales with current string translation available
        $.ajax({
          url: 'https://' + Pontoon.transifex.username + ':' + Pontoon.transifex.password + 
               '@www.transifex.net/api/2/project/' + Pontoon.transifex.project + '/resource/' + 
                Pontoon.transifex.resource + '/translation/' + locale + '/strings?key=' + original,
          dataType: 'jsonp',
          success: function(data) {
            var response = data[0];            
            if (response) {
              p.removeClass("loader no").addClass("source-string").html(self.doNotRender(response.translation));
              entity.find('.toolbar').show();
            } else {
              p.removeClass("loader").addClass("no").html('No translations yet');
              entity.find('.toolbar').hide();
            }
          }
        });
      });

      // Translation memory
      $("#main .extra .translation-memory").click(function () {
        var li = $(this).parents('.entity'),
            loader = li.find(".content .translation-memory .loader");
        if (loader.length === 0) {
          li.find(".toolbar").show();
        } else {
          $.ajax({
            url: 'http://www.frenchmozilla.fr/transvision/webservice.php',
            data: {
              recherche: li.find('.original-string .source-string').html(),
              locale: self.locale.code,
              whole_word: 'whole_word',
              repo: 'beta'
            },
            dataType: 'jsonp'
          }).error(function () {
            loader.removeClass("loader").addClass("no").html("Oops, something went wrong.");
          }).success(function (response) {
            if (response !== null) {
              // Not supported in some browsers, but needed with current JSON output:
              // https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Object/keys
              // TODO: use this kind of output - http://pastebin.mozilla.org/1316020
              Object.keys = function (obj) {
                var array = [],
                    prop;
                for (prop in obj) {
                  if (obj.hasOwnProperty(prop)) {
                    array.push(prop);
                  }
                }
                return array;
              };

              var first = response[Object.keys(response)[0]],
                  translation = first[Object.keys(first)[0]];
              loader.removeClass("loader").addClass("source-string").html(self.doNotRender(translation));
              li.find(".toolbar").show();
            } else {
              loader.removeClass("loader").addClass("no").html("No translations yet");
            }
          });
        }
      });

      // Machine translations
      // TODO: fallback if no API key provided in Pontoon.app.mt
      $("#main .extra .machine-translation").click(function () {
        var li = $(this).parents('.entity'),
            loader = li.find(".content .machine-translation .loader"),
            entity = li.get(0).entity;
        if (!self.app.mt) {
          loader.removeClass("loader").addClass("no").html("Machine translation not supported");
        } else if (loader.length === 0) {
          li.find(".toolbar").show();
        } else {
          $.ajax({
            url: "http://api.microsofttranslator.com/V2/Ajax.svc/Translate",
            dataType: 'jsonp',
            jsonp: "oncomplete",
            crossDomain: true,
            data: {
              appId: self.app.mt,
              text: entity.original,
              from: "en",
              to: self.locale.code,
              contentType: "text/html"
            }
          }).success(function(t) {
            loader.removeClass("loader").addClass("source-string").html(self.doNotRender(t));
            li.find(".toolbar").show();
          });
        }
      });

      // Copy source to translation
      $("#main .source .copy").click(function (e) {
        e.stopPropagation();
        e.preventDefault();
        var li = $(this).parents('.entity'),
            entity = li.get(0).entity,
            source = self.doRender(li.find('.source .content .active .source-string').html());

        // Only if no other entity is being edited in-place
        if (li.is('.hovered')) {
          self.common.postMessage("SAVE", source);
        // Head entities cannot be edited in-place
        } else if (!entity.body) {
          entity.translation = source;
          self.updateEntityUI(entity);
        }
      });

      // Translate in textarea
      $("#main .translation textarea").click(function (e) {
        e.stopPropagation();
        var li = $(this).parents('.entity'),
            entity = li.get(0).entity;

        // Only if no other entity is being edited in-place
        if (!li.is('.hovered') && entity.body) {
          $(this).blur();
        }
      });

      // Save translation
      $("#main .translation .save").click(function (e) {
        e.stopPropagation();
        e.preventDefault();
        var li = $(this).parents('.entity'),
            entity = li.get(0).entity,
            source = li.find('.translation textarea').val();

        // Only if no other entity is being edited in-place
        if (li.is('.hovered')) {
          self.common.postMessage("SAVE", source);
        // Head entities cannot be edited in-place
        } else if (!entity.body) {
          entity.translation = source;
          self.updateEntityUI(entity);
        }
      });

      // Cancel translation
      $("#main .translation .cancel").click(function (e) {
        e.stopPropagation();
        e.preventDefault();
        var li = $(this).parents('.entity'),
            entity = li.get(0).entity;

        // Only if no other entity is being edited in-place
        if (li.is('.hovered')) {
          self.common.postMessage("CANCEL", entity.id);
        // Head entities cannot be edited in-place
        } else if (!entity.body) {
          entity.translation = "";
          entity.ui.removeClass('translated').find('textarea').val(entity.translation);
          self.updateProgress();
        }
      });

      this.updateProgress();
    },



    /**
     * Update progress indicator and value
     */
    updateProgress: function () {
      var all = $("#entitylist .entity").length,
          translated = $("#entitylist .entity.translated").length;
      $('#progress span').width(Math.round(translated * 100 / all) + '%');
      $('#progress-value').html(translated + '/' + all);
    },



    /**
     * Update entity in the main UI
     * 
     * entity Entity
     */
    updateEntityUI: function (entity) {
      entity.ui.addClass('translated').find('textarea').val(entity.translation);
      this.updateProgress();
    },



    /**
     * Display loader text to provide feedback about the background process
     * 
     * text Loader text (e.g. Loading...)
     */
    startLoader: function (text) {
      $('#loading').html(text).removeClass().addClass('loader').show();
    },



    /**
     * Remove loader text
     * 
     * text End of operation text (e.g. Done!)
     * type [error]
     */
    endLoader: function (text, type) {
      $('#loading').html(text).removeClass('loader').addClass(type);
      setTimeout(function() {
        $('#loading').fadeOut(function() {
          $(this).empty();
        });
      }, 2000);
    },



    /**
     * Are you sure you want to leave this page?
     * In Firefox 4 and later the returned string is not displayed to the user
     *
     * enable Enables confirm leaving page dialog
     */
    confirmLeaving: function (enable) {
      window.onbeforeunload = (enable) ? function() {
        return "Your translations have not been saved.";
      } : null;
    },



    /**
     * Attach event handlers
     */
    attachHandlers: function () {
      var self = this,
          info = self.project.info,
          pages = self.project.pages;

      // General Project Info
      if (info) {
        $('#info')
          .find('.selector').show().end()
          .find('.menu')
            .find('.brief p').html(info.brief).end()
            .find('.locales p').html(info.locales).end()
            .find('.audience p').html(info.audience).end()
            .find('.metrics p').html(info.metrics);
      }

      self.confirmLeaving(true);

      // Page selector
      if (pages.length > 1) {
        $('#pontoon .page')
          .find('.selector .title').html(pages[self.project.page].title).end()
          .find('.menu').empty().end()
          .show();
          
        $(pages).each(function() {
          var count = 0,
              entities = this.entities;
          $(entities).each(function() {
            if (this.translation.length > 0) {
              count++;
            }
          });
          $('#pontoon .page .menu').append('<li>' +
            '<span class="title" data-url="' + this.url + '">' + this.title + '</span>' +
            '<span class="progress">' + Math.round(count*100/entities.length) + '%</span>' +
          '</li>');
        });

        $('#pontoon .page .menu li').click(function() {
          window.location = "?url=" + $(this).find('.title').data("url") + "&locale=" + self.locale.code;
        });
      }

      // Open/close Pontoon UI
      $('#switch').unbind("click.pontoon").bind("click.pontoon", function () {
        if ($('#main').is('.opened')) {
          $('#entitylist').height(0);
          self.common.postMessage("MODE", "Advanced");
        } else {
          $('#entitylist').height(300);
          self.common.postMessage("MODE", "Basic");
        }
        $('#source').height($(document).height() - $('#main').height());
        $('#main').toggleClass('opened');
      });

      // Authentication and profile menu
      $("#browserid").click(function() {
        self.startLoader();
        navigator.id.get(function(assertion) {
          if (assertion) {
            $.ajax({
              url: 'browserid/verify/',
              type: 'POST',
              data: {
                assertion: assertion,
                csrfmiddlewaretoken: $('#post-form input[name="csrfmiddlewaretoken"]').val()
              },
              success: function(data) {
                self.user.email = data.browserid.email;
                self.user.name = self.user.email.split("@")[0];
                self.common.postMessage("USER", self.user);
                $('#browserid').hide();
                $('#profile').find('.author').html(self.user.email).end().show();
                self.endLoader('Welcome!');
              },
              error: function() {
                self.endLoader('Oops, something went wrong.', 'error');
              }
            });
          }
        });
      });

      // Save menu
      $('#profile-menu').find('a').live("click.pontoon", function (e) {
        e.preventDefault();
        if ($(this).is(".sign-out")) {
          window.location = 'logout/'; // Without this, Enter doesn't open the link
        } else if ($(this).is(".html")) {
          self.common.postMessage("HTML");
        } else {
          self.save($(this).attr('class').split(" ")[0]);
        }
      });

      // Transifex authentication
      $('#transifex').find('.cancel').live("click.pontoon", function (e) {
        e.preventDefault();
        $('#transifex').hide();
      }).end().find('.button').live("click.pontoon", function (e) {
        e.preventDefault();
        self.save('transifex', $('#transifex form').serializeArray());
      });
    },



    /**
     * Handle messages from project code
     */
    receiveMessage: function (e) {
      if (e.source === Pontoon.project.win) {
        var message = JSON.parse(e.data);
        if (message.type === "DATA") {
          var value = message.value;
          Pontoon.project.page = value.page;
          Pontoon.project.url = value.url;
          Pontoon.project.title = value.title;
          Pontoon.project.info = value.info
          Pontoon.project.pages = $.extend(true, Pontoon.project.pages, value.pages); // Deep copy: http://api.jquery.com/jQuery.extend
          Pontoon.transifex.username = value.username;
          Pontoon.transifex.password = value.password;
          Pontoon.transifex.project = value.name;
          Pontoon.transifex.resource = value.resource;
          Pontoon.transifex.po = value.po;
        } else if (message.type === "RENDER") {
          Pontoon.attachHandlers();
          Pontoon.entityList();
          $("#spinner").fadeOut(function() {
            $("#main > header > .container").fadeIn();
          });
        } else if (message.type === "SWITCH") {
          $("#switch").click();
        } else if (message.type === "HOVER") {
          Pontoon.project.pages[Pontoon.project.page].entities[message.value].ui.addClass('hovered');
        } else if (message.type === "UNHOVER") {
          Pontoon.project.pages[Pontoon.project.page].entities[message.value].ui.removeClass('hovered');
        } else if (message.type === "ACTIVE") {
          Pontoon.project.pages[Pontoon.project.page].entities[message.value].ui.addClass('active');
        } else if (message.type === "INACTIVE") {
          Pontoon.project.pages[Pontoon.project.page].entities[message.value].ui.removeClass('active');
        } else if (message.type === "SAVE") {
          Pontoon.updateEntityUI(Pontoon.project.pages[Pontoon.project.page].entities[message.value]);
        } else if (message.type === "CANCEL") {
          var entity = Pontoon.project.pages[Pontoon.project.page].entities[message.value];
          entity.ui.removeClass('translated').find('textarea').val(entity.translation);
          Pontoon.updateProgress();
        } else if (message.type === "HTML") {
          Pontoon.save("html", message.value);
        }
      }
    },



    /**
     * Initialize Pontoon
     *
     * app Pontoon window object
     * project Website window object
     * locale ISO 639-1 language code of the language website is localized to
     */
    init: function (app, project, locale) {
      var self = this,
          email = $("#profile .author").html();
      if (!project) {
        throw "Website handler required";
      }

      // Build Pontoon object
      this.app = {
        win: app,
        path: $('base').attr('href'),
        mt: $('#server').data('mt-apikey') || ""
      };
      this.project = {
        win: project,
        url: "",
        title: "",
        info: null,
        pages: [],
        page: 0
      };
      this.locale = {
        code: locale,
        language: $("#main .language").html()
      };
      this.user = {
        email: email,
        name: email.split("@")[0]
      };
      this.transifex = {
        username: "",
        password: "",
        project: "",
        resource: "",
        po: ""
      };

      // Sync user data
      self.common.postMessage("USER", self.user);

      // Activate project code: pontoon.js (iframe cross-domain policy solution)
      self.common.postMessage("INITIALIZE", {
        locale: self.locale,
        path: self.app.path,
        transifex: self.transifex
      });

      // Wait for project code messages
      // TODO: display page not ready for Pontoon notification if event not triggered
      window.addEventListener("message", self.receiveMessage, false);
    },



    /**
     * Update slider position in the menu
     * 
     * menu Menu element
     */
    updateSlider: function (menu) {
      var hovered = menu.find('li.hover');

      var maxHeight = menu.height();
      var visibleTop = menu.scrollTop();
      var visibleBottom = visibleTop + maxHeight;
      var hoveredTop = visibleTop + hovered.position().top;
      var hoveredBottom = hoveredTop + hovered.outerHeight();

      if (hoveredBottom >= visibleBottom) {
        menu.scrollTop(Math.max(hoveredBottom - maxHeight, 0));
      } else if (hoveredTop < visibleTop) {
        menu.scrollTop(hoveredTop);
      }
    },



    /**
     * Common functions used in both, client specific code and Pontoon library
     */
    common: (function () {
      // Show/hide menu on click
      $('.selector').live("click.pontoon", function (e) {
        if (!$(this).siblings('.menu').is(':visible')) {
          e.stopPropagation();
          $('.menu').hide();
          $('.select').removeClass('opened');
          $('#iframe-cover').hide(); // iframe fix
          $(this).siblings('.menu').show().end()
                 .parents('.select').addClass('opened');
          $('#iframe-cover').show().height($('#source').height()); // iframe fix
        }
      });

      // Hide menus on click outside
      $('html').live("click.pontoon", function () {
        $('.menu').hide();
        $('#iframe-cover').hide(); // iframe fix
        $('.select').removeClass('opened');
      });

      // Confirm and select locale handlers
      $('.locale .confirm, .locale .menu li').unbind("click.pontoon").bind("click.pontoon", function () {
        var locale = $(this).find('.language').attr('class').split(' ')[1],
            url = $('.url:visible').val();
        if (url) {
          window.location = '/locale/' + locale + '/url/' + url + '/';
        } else {
          Pontoon.common.showError("Please enter the URL first.");
          $('.url:visible').focus();
        }
      });
      $('.url').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        var key = e.keyCode || e.which;
        if (key === 13) { // Enter
          $('.locale .confirm:visible').click();
          return false;
        }
      });

      // Menu hover
      $('.menu li').live('hover', function () {
        $('.menu li.hover').removeClass('hover');
        $(this).toggleClass('hover');
      });

      // Add case insensitive :contains-like selector to jQuery (needed for locale search)
      $.expr[':'].containsi = function(a,i,m){
        return (a.textContent || a.innerText || '').toUpperCase().indexOf(m[3].toUpperCase())>=0;
      };

      // Reset locale search
      $('.locale .selector').live('click.pontoon', function() {
        $('.search').val('').focus().siblings('ul').scrollTop(0).find('.no-match').hide().siblings().removeClass('hover').show();
      });

      // Search locales
      $('.search').live("click.pontoon", function (e) {
        e.stopPropagation();
      }).live("keyup.pontoon", function(e) {
        var ul = $(this).siblings('ul'),
            val = $(this).val();
        ul
          .find('li').show().end()
          .find('li:not(":containsi("' + val + '")")').hide();
        if (ul.find('li:not(".no-match"):visible').length === 0) {
          ul.find('.no-match').find('span').html(val).end().show();
        } else {
          ul.find('.no-match').hide();
        }
      });

      // Use arrow keys to move around menu, confirm with enter, close with escape
      $('html').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        if ($('.menu').is(':visible')) {
          var key = e.keyCode || e.which,
              menu = $('.menu:visible'),
              hovered = menu.find('li.hover');

          if (key === 38) { // up arrow
            if (hovered.length === 0 || menu.find('li:visible:first').is('.hover')) {
              menu.find('li.hover').removeClass('hover');
              menu.find('li:visible:last').addClass('hover');
            } else {
              menu.find('li.hover').removeClass('hover').prev(':visible').addClass('hover');
            }
            Pontoon.updateSlider(menu.find('ul'));
            return false;
          }

          if (key === 40) { // down arrow
            if (hovered.length === 0 || menu.find('li:visible:last').is('.hover')) {
              menu.find('li.hover').removeClass('hover');
              menu.find('li:visible:first').addClass('hover');
            } else {
              menu.find('li.hover').removeClass('hover').next(':visible').addClass('hover');
            }
            Pontoon.updateSlider(menu.find('ul'));
            return false;
          }

          if (key === 13) { // Enter
            var a = hovered.find('a');
            if (a.length > 0) {
              a.click();
            } else {
              hovered.click();
            }
            return false;
          }

          if (key === 27) { // Escape
            menu.siblings('.selector').click();
            return false;
          }
        }
        if ($('.popup').is(':visible')) {
          var key = e.keyCode || e.which,
              popup = $('.popup:visible');

          if (key === 13) { // Enter
            popup.find('.button').click();
            return false;
          }
        }
      });

      return {
        /*
         * Show error message
         *
         * message Error message to be displayed
         */
        showError: function(message) {
          var error = message || 'Oops, website is either not supported by Pontoon or could not be found.';
          $('.notification')
            .html(error)
            .addClass('error')
            .css('visibility', 'visible').show();
        },
        /*
         * window.postMessage improved
         *
         * messageType data type to be sent to the other window
         * messageValue data value to be sent to the other window
         * otherWindow reference to another window
         * targetOrigin specifies what the origin of otherWindow must be
         */
        postMessage: function (messageType, messageValue, otherWindow, targetOrigin) {
          var otherWindow = otherWindow || Pontoon.project.win,
              targetOrigin = targetOrigin || "*",
              message = {
                type: messageType,
                value: messageValue
              }
          otherWindow.postMessage(JSON.stringify(message), targetOrigin);
        }
      }
    })()

  };
}());
