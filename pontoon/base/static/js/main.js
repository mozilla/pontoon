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

      // Generate PO file object
      function getPO() {
        var po = {
            metadata: {
                'project_title': self.project.title,
                'locale_language': self.locale.language,
                'username': self.user.name,
                'user_email': self.user.email
            },
            translations: {}
        }

        $(self.project.entities).each(function () {
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

        return po;
      }

      // It is impossible to download files with AJAX
      function download(params) {
        params.csrfmiddlewaretoken = $('#server').data('csrf');
        var post = $('<form>', {
          method: 'post',
          action: 'download/'
        });
        for(var key in params) {
          $('<input>', {
            type: 'hidden',
            name: key,
            value: params[key]
          }).appendTo(post);
        }
        post.appendTo('body').submit().remove();
      }

      if (type === "html") {
        params.content = value;
        download(params);

      } else if (type === "json") {
        // Deep copy: http://api.jquery.com/jQuery.extend
        var entities = $.extend(true, [], this.project.entities);
        $(entities).each(function () {
          delete this.ui;
          delete this.hover;
          delete this.unhover;
          delete this.id;
          delete this.body;
        });
        params.content = JSON.stringify(entities, null, "\t");
        download(params);

      } else if (type === "po") {
        params.content = JSON.stringify(getPO());
        download(params);

      } else if (type === "properties") {
        params.content = self.project.url;
        download(params);

      } else if (type === "transifex") {
        self.startLoader();

        params.strings = [];
        $("#entitylist .translated").each(function() {
          var entity = $(this)[0].entity;
          params.strings.push({
            original: entity.original,
            translation: entity.translation
          });
        });

        params.url = self.project.url;

        if (value) {
          params.auth = {
            username: value[0].value,
            password: value[1].value,
            remember: value[2] ? 1 : 0
          };
        }

        $.ajax({
          url: 'transifex/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            data: JSON.stringify(params)
          },
          success: function(data) {
            if (data === "authenticate") {
              self.endLoader();
              $("#transifex").show();
            } else if (data === "200") {
              self.endLoader('Done!');
              $('#transifex').hide();
            } else if (data === "error") {
              self.endLoader('Oops, something went wrong.', 'error');
              $('#transifex').hide();
            }
          },
          error: function() {
            self.endLoader('Oops, something went wrong.', 'error');
            $('#transifex').hide();
          }
        });

      } else if (type === "svn") {
        self.startLoader();

        params.content = JSON.stringify(getPO());
        params.url = self.project.url;

        if (value) {
          params.auth = {
            username: value[0].value,
            password: value[1].value,
            remember: value[2] ? 1 : 0
          };
        }

        $.ajax({
          url: 'svn/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            data: JSON.stringify(params)
          },
          success: function(data) {
            if (data === "authenticate") {
              self.endLoader();
              $("#svn").show();
            } else if (data === "200") {
              self.endLoader('Done!');
              $('#svn').hide();
            } else if (data === 'error') {
              self.endLoader('Oops, something went wrong.', 'error');
              $('#svn').hide();
            }
          },
          error: function() {
            self.endLoader('Oops, something went wrong.', 'error');
            $('#svn').hide();
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
          list = $('#entitylist').append('<ul class="editables"></ul>'),
          localeMenu = $('.locale .menu').html();

      // Render
      $(self.project.entities).each(function () {
        var li = $('<li class="entity' + 
          // append classes to translated and uneditable entities
          (this.translation ? ' translated' : '') + 
          (!this.body ? ' uneditable' : '') + '">' + 
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
              '<a href="#cancel" class="cancel" title="Cancel"></a>' +
            '</div>' +
          '</div>' +
        '</div></li>', self.app.win);

        li.get(0).entity = this;
        this.ui = li; /* HTML Element representing string in the main UI */

        list.find('.editables').append(li);
      });

      // Move uneditable entities to a separate list
      var uneditables = $(".entity.uneditable");
      if (uneditables.length > 0) {
        list.find('.editables').after('<h2>Strings not found on the current page</h2><ul class="uneditables"></ul>');
        uneditables.appendTo("#entitylist ul.uneditables")
      }

      // Main entity list handlers
      $("#main .entity:not('.uneditable')").hover(function () {
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
        $('.search:visible').focus();
      });
      $("#main .source .other-locales .select .menu li").click(function (e) {
        e.stopPropagation();
        var li = $(this),
            entity = li.parents(".entity"),
            original = entity[0].entity.original,
            p = li.parents('.select').next('p').show();

        p.addClass("loader").html('');
        li.parents('.menu').siblings('.selector')
          .find('.language').attr('class', li.find('.language').attr('class')).html(li.find('.language').contents()[0].nodeValue).end().end()
        .hide();

        $.ajax({
          url: 'get/',
          data: {
            locale: li.find(".language").attr("class").split(" ")[1],
            pk: self.project.pk,
            original: original
          },
          success: function(data) {
            if (data !== "error") {
              p.removeClass("loader no").addClass("source-string").html(self.doNotRender(data));
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
            url: 'http://transvision.mozfr.org/index.php',
            data: {
              recherche: li.find('.original-string .source-string').html(),
              locale: self.locale.code,
              whole_word: 'whole_word',
              repo: 'aurora',
              json: 'true'
            },
            dataType: 'jsonp'
          }).error(function () {
            loader.removeClass("loader").addClass("no").html("Oops, something went wrong.");
          }).success(function (response) {
            if (response !== null) {
              // Not supported in some browsers, but needed with current JSON output:
              // https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Object/keys
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
      $("#main .extra .machine-translation").click(function () {
        var li = $(this).parents('.entity'),
            loader = li.find(".content .machine-translation .loader"),
            entity = li.get(0).entity,
            mt = $('#server').data('mt-apikey');
        if (!mt) {
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
              appId: mt,
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
          self.updateOnServer(entity);
        }
      });

      // Translate in textarea
      $("#main .translation textarea").focus(function (e) {
        var li = $(this).parents('.entity');

        // Only if no other entity is being edited in-place
        if (!li.is('.hovered') && li.get(0).entity.body) {
          $(this).blur();
        }
      // Keyboard navigation in textarea
      }).unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        var key = e.keyCode || e.which,
            li = $(this).parents('.entity');

        if (key === 13) { // Enter: confirm translation
          li.find('.save').click();
          return false;
        }

        if (key === 27) { // Esc: status quo
          li.find('.cancel').click();
          return false;
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
          if (source !== '') {
            self.common.postMessage("SAVE", source);
          } else {
            self.common.postMessage("DELETE");
          }
        // Head entities cannot be edited in-place
        } else if (!entity.body) {
          if (source !== '') {
            entity.translation = source;
            self.updateEntityUI(entity);
            self.updateOnServer(entity);
          } else {
            entity.translation = '';
            entity.ui.removeClass('translated');
            self.updateProgress();
            self.updateOnServer(entity);
          }
        }
      });

      // Do not change anything when cancelled
      $("#main .translation .cancel").click(function (e) {
        e.stopPropagation();
        e.preventDefault();
        var li = $(this).parents('.entity'),
            entity = li.get(0).entity,
            textarea = li.find('.translation textarea');

        // Only if no other entity is being edited in-place
        if (li.is('.hovered')) {
          textarea.val(entity.translation || entity.orignal);
          self.common.postMessage("CANCEL", entity.id);
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
      if (entity.translation === '') {
        entity.ui.removeClass('translated');
      }
      this.updateProgress();
    },



    /**
     * Update entity translation on server
     * 
     * entity Entity
     */
    updateOnServer: function (entity) {
      var self = this;
      if (self.user.email && self.project.pk) {
        self.startLoader();
        $.ajax({
          url: 'update/',
          data: {
            locale: self.locale.code,
            pk: self.project.pk,
            original: entity.original,
            translation: entity.translation
          },
          success: function(data) {
            if (data !== "error") {
              self.endLoader('Translation ' + data + '!');
            } else {
              self.endLoader('Oops, something went wrong.', 'error');
            }
          },
          error: function() {
            self.endLoader('Oops, something went wrong.', 'error');
          }
        });
      }
    },



    /**
     * Display loader to provide feedback about the background process
     */
    startLoader: function () {
      $('#loading').removeClass().addClass('loader').show();
    },



    /**
     * Remove loader
     * 
     * text End of operation text (e.g. Done!)
     * type [error]
     */
    endLoader: function (text, type) {
      $('#loading').removeClass('loader');
      if (text) {
        $('.notification').html(text).addClass(type).show();
      }
      setTimeout(function() {
        $('.notification').fadeOut(function() {
          $(this).attr('class', 'notification').empty();
        });
      }, 2000);
    },



    /**
     * Attach event handlers
     */
    attachHandlers: function () {
      var self = this;

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
              url: 'browserid/',
              type: 'POST',
              data: {
                assertion: assertion,
                csrfmiddlewaretoken: $('#server').data('csrf')
              },
              success: function(data) {
                // After AJAX-based authentication, CSRF token needs to be updated
                $.get("csrf/", function(csrf_token) {
                  $('#server').data('csrf', csrf_token);
                });
                self.user.email = data.browserid.email;
                self.user.name = self.user.email.split("@")[0];
                self.common.postMessage("USER", self.user);
                $('#browserid').hide();
                $('#profile').find('.author').html(self.user.email).end().show();
                if (data.manager) {
                  $('#profile-menu .sign-out').parent().after('<li><a class="admin" href="admin/">Admin</a></li>');
                }
                self.endLoader('Welcome!');
              },
              error: function() {
                self.endLoader('Oops, something went wrong.', 'error');
              }
            });
          } else {
            self.endLoader();
          }
        });
      });

      // Save menu
      $('#profile-menu').find('a').live("click.pontoon", function (e) {
        e.preventDefault();
        if ($(this).is(".sign-out")) {
          window.location = 'signout/'; // Without this, Enter doesn't open the link
        } else if ($(this).is(".admin")) {
          window.location = 'admin/'; // Without this, Enter doesn't open the link
        } else if ($(this).is(".html")) {
          self.common.postMessage("HTML");
        } else {
          self.save($(this).attr('class').split(" ")[0]);
        }
      });

      // Transifex and SVN authentication
      $('.popup').find('.cancel').live("click.pontoon", function (e) {
        e.preventDefault();
        $('.popup').hide();
      }).end().find('.button').live("click.pontoon", function (e) {
        e.preventDefault();
        var type = $(this).parents('.popup').attr('id');
        self.save(type, $('#' + type + ' form').serializeArray());
      });
    },



    /**
     * Handle messages from project code
     */
    receiveMessage: function (e) {
      if (e.source === Pontoon.project.win) {
        var message = JSON.parse(e.data);
        if (message.type === "DATA") {
          // Deep copy: http://api.jquery.com/jQuery.extend
          Pontoon.project.entities = $.extend(true, Pontoon.project.entities, message.value.entities);
        } else if (message.type === "RENDER") {
          var value = message.value;
          Pontoon.project.url = value.url;
          Pontoon.project.title = value.title;
          Pontoon.project.type = value.type;
          Pontoon.attachHandlers();
          Pontoon.entityList();
          $("#spinner").fadeOut(function() {
            $("#main > header > .container").fadeIn();
          });
          if (Pontoon.project.type !== 'webL10n') {
            $('#profile-menu .properties').parent().remove();
          }
        } else if (message.type === "ERROR") {
          var msg = message.value || 'Oops, something went wrong. Refresh to try again.';
          Pontoon.common.showError(msg);
          $("#progress, #switch, #drag").remove();
          $("#spinner").fadeOut(function() {
            $("#main > header > .container").fadeIn();
          });
          Pontoon.attachHandlers();
        } else if (message.type === "SWITCH") {
          $("#switch").click();
        } else if (message.type === "HOVER") {
          Pontoon.project.entities[message.value].ui.addClass('hovered');
        } else if (message.type === "UNHOVER") {
          Pontoon.project.entities[message.value].ui.removeClass('hovered');
        } else if (message.type === "ACTIVE") {
          Pontoon.project.entities[message.value].ui.addClass('active');
        } else if (message.type === "INACTIVE") {
          Pontoon.project.entities[message.value].ui.removeClass('active');
        } else if (message.type === "UPDATE") {
          var entity = Pontoon.project.entities[message.value];
          Pontoon.updateEntityUI(entity);
          Pontoon.updateOnServer(entity);
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
        path: $('base').attr('href'), // pontoon.css injection
        external: $('#server').data('external'),
        links: $('#server').data('links')
      };
      this.project = {
        win: project,
        url: "",
        title: "",
        entities: [],
        pk: $('#server').data('id'),
        type: 'gettext'
      };
      this.locale = {
        code: locale,
        language: $("#main .language").contents()[0].nodeValue // PO file
      };
      this.user = {
        email: email,
        name: email.split("@")[0] // PO file
      };

      // Sync user data
      self.common.postMessage("USER", self.user);

      // Activate project code: pontoon.js (iframe cross-domain policy solution)
      self.common.postMessage("INITIALIZE", {
        locale: self.locale,
        path: self.app.path,
        external: self.app.external,
        links: self.app.links,
        pk: self.project.pk
      });

      // Wait for project code messages
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
          $('.menu, .popup').hide();
          $('.select').removeClass('opened');
          $('#iframe-cover').hide(); // iframe fix
          $(this).siblings('.menu').show().end()
                 .parents('.select').addClass('opened');
          $('#iframe-cover').show().height($('#source').height()); // iframe fix
        }
      });

      // Hide menus on click outside
      $('body:not(".admin-form")').live("click.pontoon", function () {
        $('.menu').hide();
        $('#iframe-cover').hide(); // iframe fix
        $('.select').removeClass('opened');
      });

      // Confirm and select locale handlers
      $('.locale .confirm, .locale .menu li:not(".no-match")').unbind("click.pontoon").bind("click.pontoon", function () {
        var locale = $(this).find('.language').attr('class').split(' ')[1],
            url = $('.url:visible').val();

        $('.locale .button .language').attr('class', 'language ' + locale).html($('.locale .menu .language.' + locale).html());
        if (url) {
          window.location = '/locale/' + locale + '/site/' + escape(url) + (url[url.length-1] !== '/' ? '/' : '');
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

      // Project menu handler
      $('.project .menu li').live("click.pontoon", function () {
        $('.url').val($(this).find('.project-url').html());
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

      // Focus locale search
      $('.locale .selector').live('click.pontoon', function() {
        $('.search:visible').focus();
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

      // Search projects
      $('.url').live("keyup.pontoon", function(e) {
        var menu = $(this).siblings('.menu'),
            ul = menu.find('ul'),
            val = $(this).val();

        if (val !== '') {
          ul
            .find('li').addClass('match').end()
            .find('li:not(":containsi("' + val + '")")').removeClass('match');

          if (ul.find('li.match').length === 0) {
            menu.hide().parent().removeClass('opened');
          } else {
            menu.show().parent().addClass('opened');
          }
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
            if (menu.parent().is('.locale')) {
              Pontoon.updateSlider(menu.find('ul'));
            }
            if (menu.parent().is('.project')) {
              $('.url').val($('.project .menu li.hover').find('.project-url').html());
            }
            return false;
          }

          if (key === 40) { // down arrow
            if (hovered.length === 0 || menu.find('li:visible:last').is('.hover')) {
              menu.find('li.hover').removeClass('hover');
              menu.find('li:visible:first').addClass('hover');
            } else {
              menu.find('li.hover').removeClass('hover').next(':visible').addClass('hover');
            }
            if (menu.parent().is('.locale')) {
              Pontoon.updateSlider(menu.find('ul'));
            }
            if (menu.parent().is('.project')) {
              $('.url').val($('.project .menu li.hover').find('.project-url').html());
            }
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
          if (key === 27) { // Escape
            popup.find('.cancel').click();
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
          $('.notification')
            .html(message)
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
