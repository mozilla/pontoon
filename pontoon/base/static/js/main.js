var Pontoon = (function () {

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

      function strip(entities) {
        // Deep copy: http://api.jquery.com/jQuery.extend
        var e = $.extend(true, [], entities);
        $(e).each(function () {
          delete this.ui;
          delete this.hover;
          delete this.unhover;
          delete this.id;
          delete this.pk;
          delete this.body;
        });
        return e;
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
        var entities = strip(this.project.entities);
        params.content = JSON.stringify(entities, null, "\t");
        download(params);

      } else if (type === "zip") {
        params.content = self.project.pk;
        download(params);

      } else if (type === "transifex") {
        self.startLoader();

        params.strings = [];
        $("#entitylist .approved").each(function() {
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

        params.pk = self.project.pk;

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
            if (data.type === "authenticate") {
              self.endLoader(data.message);
              $("#svn").show();

              // Move notification up
              var temp = $('.notification').css('top');
              $('.notification').css('top', '+=' + $('#svn').outerHeight());
              setTimeout(function() {
                $('.notification').css('top', temp);
              }, 2400); // Wait for close + fadeout

            } else if (data === "200") {
              self.endLoader('Done!');
              $('#svn').hide();

            } else if (data.type === "error") {
              self.endLoader(data.message, 'error', true);
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
     * Get translations to other locales of given entity
     *
     * entity Entity
     */
    getOtherLocales: function (entity) {
      var self = this,
          list = $('#other-locales ul').empty();

      $.ajax({
        url: 'other-locales/',
        data: {
          entity: entity.pk,
          locale: self.locale.code
        },
        success: function(data) {
          if (data !== "error") {
            $.each(data, function() {
              list.append('<li title="Click to copy">' +
                '<header>' + this.locale.name + '<span class="stress">' + this.locale.code + '</span></header>' +
                '<p class="translation">' + self.doNotRender(this.translation) + '</p>' +
              '</li>');
            });
          } else {
            list.append('<li class="disabled"><p>No translations available.</p></li>');
          }
        }
      });
    },



    /*
     * Get suggestions from machine translation and translation memory
     *
     * original Original string
     */
    getMachinery: function (original) {
      var self = this,
          mt = $('#machinery .machine-translation .translation'),
          tm = $('#machinery .translation-memory .translation')
            .empty()
            .addClass('loader');

      $('#machinery li')
        .removeClass('disabled')
        .parent().removeAttr('title');

      // Machine translation
      if (self.locale.notSupported) {
        mt.html("Oops, target language not supported.")
          .parent().addClass('disabled');

      } else {
        mt.empty()
          .addClass('loader');

        // On first run, check if target language supported
        var check = false;
        if (self.locale.notSupported === undefined) {
          check = true;
        }

        $.ajax({
          url: 'machine-translation/',
          data: {
            text: original,
            locale: self.locale.code,
            check: check
          }

        }).error(function() {
          mt.removeClass("loader")
            .html("Oops, something went wrong.")
            .parent().addClass('disabled');

        }).success(function(data) {
          self.locale.notSupported = false;
          mt.removeClass("loader");

          if (data.translation) {
            mt.html(self.doNotRender(data.translation))
              .parent().attr('title', 'Click to copy');

          } else {
            var error = "Oops, something went wrong.";

            if (data === "apikey") {
              error = "Oops, machine translation not supported.";
            } else if (data === "not-supported") {
              error = "Oops, target language not supported.";
              self.locale.notSupported = true;
            }

            mt.html(error)
              .parent().addClass('disabled');
          }
        });
      }

      // Translation memory
      $.ajax({
        url: 'translation-memory/',
        data: {
          text: original,
          locale: self.locale.code
        }

      }).error(function() {
        tm.removeClass("loader")
          .html("Oops, something went wrong.")
          .parent().addClass('disabled');

      }).success(function(data) {
        tm.removeClass("loader");
        if (data.translation) {
          tm.html(self.doNotRender(data.translation))
          .parent().attr('title', 'Click to copy');
        } else {
          var error = (data === "no") ?
            "No translations available." :
            "Oops, something went wrong.";
          tm.html(error)
            .parent().addClass('disabled');
        }
      });
    },



    /*
     * Get history of translations of given entity
     *
     * entity Entity
     */
    getHistory: function (entity) {
      var self = this,
          list = $('#history ul').empty();

      $.ajax({
        url: 'get-history/',
        data: {
          entity: entity.pk,
          locale: self.locale.code
        },
        success: function(data) {
          if (data !== "error") {
            $.each(data, function() {
              list.append(
                '<li data-id="' + this.id + '" ' +
                (this.approved ? ' class="approved"' : '') +
                'title="Click to copy">' +
                  '<header class="clearfix' +
                    ((self.user.localizer) ? ' localizer' :
                      ((self.user.email === this.user && !this.approved) ?
                        ' own' : '')) +
                    '">' +
                    '<div class="info">' +
                      (this.user || "Imported") +
                      '<span class="stress">' + this.date + '</span>' +
                    '</div>' +
                    '<menu class="toolbar">' +
                      '<button class="approve" title="' +
                      (this.approved ? '' : 'Approve') +
                      '"></button>' +
                      '<button class="delete" title="Delete"></button>' +
                    '</menu>' +
                  '</header>' +
                  '<p class="translation">' +
                    self.doNotRender(this.translation) +
                  '</p>' +
                '</li>');
            });
          } else {
            list.append('<li class="disabled"><p>No translations available.</p></li>');
          }
        }
      });
    },



    /*
     * Open translation editor in the main UI
     *
     * entity Entity
     */
    openEditor: function (entity) {
      $('#original').html(this.doNotRender(entity.original));
      $('#comment').html(entity.comment);
      $('#translation').val(entity.translation);

      var original = entity.original.length,
          translation = entity.translation.length;

      $('#translation-length')
        .show() // Needed if advanced features opened by default
        .find('.original-length').html(original).end()
        .find('.current-length').html(translation);

      this.getHistory(entity);
      $("#helpers nav a:first").click();
      $("#editor")[0].entity = entity;

      $("#entitylist .hovered").removeClass('hovered');
      entity.ui.addClass('hovered');

      // Open advanced features by default if project requests them
      if (this.project.win && !this.project.width) {
        $("#entitylist")
          .css('left', -$('#sidebar').width()/2);

        $("#editor")
          .addClass('opened')
          .css('left', 0);
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
     * Render list of entities to translate
     */
    renderEntityList: function () {
      var self = this,
          list = $('#entitylist').append(
            '<input id="search" type="search" placeholder="Search text to translate">' +
            '<div class="wrapper">' +
              '<ul class="editables"></ul>' +
              ((self.project.win) ?
                '<h2 id="not-on-page">Not on the current page</h2>' : '') +
              '<ul class="uneditables"></ul>' +
              '<h3 class="no-match"><div>ఠ_ఠ</div>No results.</h3>' +
            '</div>');

      // Search entities
      $('#search').keyup(function(e) {
        var ul = $('#entitylist .wrapper > ul'),
            val = $(this).val();

        ul
          .find('li').show().end()
          .find('.source-string' + ':not(":containsi("' + val + '")")').parent().hide();

        if ($('.uneditables li:visible').length === 0) {
          $('#not-on-page').hide();
        } else {
          $('#not-on-page').show();
        }

        if (ul.find('li:visible').length === 0) {
          $('#entitylist .no-match').show();
        } else {
          $('#entitylist .no-match').hide();
        }
      });

      // Render
      $(self.project.entities).each(function () {
        var li = $('<li class="entity' + 
          // append classes to translated, approved and uneditable entities
          (this.approved ? ' approved' : (this.translation ? ' translated' : '')) +
          (!this.body ? ' uneditable' : '') + '">' +
          '<span class="status"></span>' +
          '<p class="source-string">' + self.doNotRender(this.original) + '</p>' +
        '</li>', self.app.win);

        li[0].entity = this;
        this.ui = li; /* HTML Element representing string in the main UI */

        if (this.body) {
          list.find('.editables').append(li);
        } else {
          list.find('.uneditables').append(li);
        }
      });

      // Move uneditable entities to a separate list
      if (list.find('.editables li').length === 0) {
        list.find('.editables').remove();
      } else if ($(".entity.uneditable").length === 0) {
        list.find('.uneditables, h2').remove();
      }

      // Hover editable entities on the page
      $("#entitylist .entity:not('.uneditable')").hover(function () {
        self.common.postMessage("HOVER", this.entity.id);
      }, function () {
        self.common.postMessage("UNHOVER", this.entity.id);
      });

      // Open entity editor on click
      $("#entitylist .entity").click(function () {
        var entity = this.entity;

        if ($(this).is(':not(".uneditable")')) {
          self.common.postMessage("EDIT");
        } else {
          self.openEditor(entity);
        }
      });
    },



    /*
     * Attach event handlers to editor elements
     */
    attachEditorHandlers: function () {
      var self = this;

      // Top bar
      $("#topbar > a").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var sec = $(this).attr('id'),
            entity = $('#editor')[0].entity,
            entitySelector = '#entitylist .entity',
            index = entity.ui.index(entitySelector);

        switch (sec) {
          case "back":
            $('#cancel').click();
            break;

          case "previous":
            var prev = $(entitySelector).eq(index - 1);
            if (prev.length === 0) {
              prev = $('#entitylist ul > li:last');
            }
            var newEntity = prev[0].entity;
            if (newEntity.body || entity.body) {
              self.common.postMessage("NAVIGATE", newEntity.id);
            }
            if (!newEntity.body) {
              self.openEditor(newEntity);
            }
            break;

          case "next":
            var next = $(entitySelector).eq(index + 1);
            if (next.length === 0) {
              next = $('#entitylist ul > li:first');
            }
            var newEntity = next[0].entity;
            if (newEntity.body || entity.body) {
              self.common.postMessage("NAVIGATE", newEntity.id);
            }
            if (!newEntity.body) {
              self.openEditor(newEntity);
            }
            break;
        }
      });

      // Translate in textarea
      $("#translation").unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        var key = e.keyCode || e.which;

        // Enter: save translation
        if (key === 13) {
          $('#save').click();
          return false;
        }

        // Esc: cancel
        if (key === 27) {
          if (self.project.win && !self.project.width) {
            $('#cancel').click();
          }
          return false;
        }

      // Update length (keydown is triggered too early)
      }).unbind("input propertychange").bind("input propertychange", function (e) {
        var length = $('#translation').val().length;
        $('#translation-length .current-length').html(length);
      });

      // Copy source to translation
      $("#copy").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var original = $('#original').html(),
            source = self.doRender(original);
        $('#translation').val(source).focus();
        $('#translation-length .current-length').html(source.length);
      });

      // Clear translation area
      $("#clear").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        $('#translation').val('').focus();
        $('#translation-length .current-length').html('0');
      });

      // Do not change anything when cancelled
      $('#cancel').click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $("#editor")[0].entity;

        // Save entity if dirty - cannot be automatically synced with backend
        if (entity.dirty) {
          entity.dirty = false;
          $('#save').click();
        }

        $("#entitylist")
          .css('left', 0)
          .find('.hovered').removeClass('hovered');

        $("#editor")
          .removeClass('opened')
          .css('left', $('#sidebar').width());

        if (entity.body) {
          self.common.postMessage("CANCEL");
          self.common.postMessage("UNHOVER", entity.id);
        }
      });

      // Save translation
      $('#save').click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $('#editor')[0].entity,
            source = $('#translation').val();

        if (source === '') {
          self.endLoader('Empty translations cannot be submitted.', 'error');
          return;
        }

        // Update translation, including in-place if possible
        if (entity.body && (self.user.localizer || !entity.approved)) {
          self.common.postMessage("SAVE", source);
        } else {
          self.updateOnServer(entity, source);
        }
      });

      // Helpers navigation
      $("#helpers nav a").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        $("#helpers nav li").removeClass('active');
        $(this).parent().addClass('active');

        var sec = $(this).attr('href').substr(1),
            editor = $('#editor')[0],
            entity = editor.entity;

        switch (sec) {
          case "machinery":
            if (editor.machinery != entity.id) {
              self.getMachinery(entity.original);
              editor.machinery = entity.id;
            }
            break;

          case "other-locales":
            if (editor.otherLocales != entity.id) {
              self.getOtherLocales(entity);
              editor.otherLocales = entity.id;
            }
            break;
        }

        $("#helpers > section").hide();
        $("#helpers > section#" + sec).show();
      });

      // Copy helpers result to translation
      $("#helpers li:not('.disabled')").live("click", function (e) {
        e.stopPropagation();
        e.preventDefault();

        var translation = $(this).find('.translation').html(),
            source = self.doRender(translation);
        $('#translation').val(source).focus();
        $('#translation-length .current-length').html(source.length);
      });

      // Restore clickable links
      $("#helpers li > a").live("click", function (e) {
        e.stopPropagation();
      });

      // Approve and delete translations
      $("#history menu button").live("click", function (e) {
        var button = $(this);
        if (button.is('.approve') && button.parents('li.approved').length > 0) {
          return;
        }

        e.stopPropagation();
        e.preventDefault();

        $.ajax({
          url: $(this).attr('class') + '-translation/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            translation: $(this).parents('li').data('id')
          },
          success: function(data) {
            if (data.type === "approved") {
              button.parents('li')
                .addClass('approved').click()
                .siblings().removeClass('approved');
              $('#save').click();

            } else if (data.type === "deleted") {
              var item = button.parents('li'),
                  index = item.index();
              item.remove();
              self.endLoader('Translation deleted');

              // Active translation deleted
              if (index === 0) {
                var entity = $('#editor')[0].entity,
                    next = $('#history li[data-id="' + data.next + '"]');

                // Make newest alternative translation active
                if (next.length > 0) {
                  next.click();
                  entity.dirty = true;

                // Last translation deleted, no alternative available
                } else {
                  entity.dirty = false;
                  $('#translation').val('').focus();
                  if (entity.body) {
                    self.common.postMessage("DELETE");
                  } else {
                    entity.approved = false;
                    entity.translation = "";
                    self.updateEntityUI(entity);
                  }
                  $('#history ul')
                    .append('<li class="disabled">' +
                              '<p>No translations available.</p>' +
                            '</li>');
                }
              }
            } else {
              self.endLoader('Oops, something went wrong.', 'error');
            }
          },
          error: function() {
            self.endLoader('Oops, something went wrong.', 'error');
          }
        });
      });
    },



    /*
     * Update progress indicator and value
     */
    updateProgress: function () {
      var all = $("#entitylist .entity").length,
          translated = $("#entitylist .entity.translated").length,
          approved = $("#entitylist .entity.approved").length,
          percentTranslated = Math.round(translated * 100 / all),
          percentApproved = Math.round(approved * 100 / all);

      $('#progress .translated').width(percentTranslated + '%');
      $('#progress .approved').width(percentApproved + '%');
      $('#progress .number').html(approved + '|' + all);

      if (percentTranslated + percentApproved > 50) {
        $('#progress .number').addClass('left');
      } else {
        $('#progress .number').removeClass('left');
      }
    },



    /*
     * Update entity in the main UI
     * 
     * entity Entity
     */
    updateEntityUI: function (entity) {
      entity.ui.removeClass('translated approved');
      if (entity.approved) {
        entity.ui.addClass('approved');
      } else if (entity.translation !== '') {
        entity.ui.addClass('translated');
      }
      this.updateProgress();
    },



    /*
     * Update entity translation on server
     * 
     * entity Entity
     * translation Translation
     */
    updateOnServer: function (entity, translation) {
      var self = this;
      self.startLoader();
      $.ajax({
        url: 'update/',
        type: 'POST',
        data: {
          csrfmiddlewaretoken: $('#server').data('csrf'),
          locale: self.locale.code,
          entity: entity.pk,
          translation: translation
        },
        success: function(data) {
          if (data.type) {
            self.endLoader('Translation ' + data.type);
            entity.translation = data.translation;
            entity.approved = data.approved;
            self.updateEntityUI(entity);
            if (self.project.win && !self.project.width &&
                $("#editor").is('.opened')) {
              $('#cancel').click();
            } else if (!self.project.win || self.project.width) {
              $('#next').click();
            }
          } else if (data === "error") {
            self.endLoader('Oops, something went wrong.', 'error');
          } else {
            self.endLoader(data, 'error');
          }
        },
        error: function() {
          self.endLoader('Oops, something went wrong.', 'error');
        }
      });
    },



    /*
     * Close notification
     */
    closeNotification: function () {
      $('.notification').fadeOut(function() {
        $(this).attr('class', 'notification').empty();
      });
    },



    /*
     * Display loader to provide feedback about the background process
     */
    startLoader: function () {
      $('#loading').removeClass().addClass('loader').show();
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
        $('.notification').html(text).addClass(type).show().click(function() {
          Pontoon.closeNotification();
        });
      }
      if (!persist) {
        setTimeout(function() {
          Pontoon.closeNotification();
        }, 2000);
      }
    },



    /*
     * Attach event handlers to main toolbar elements
     */
    attachMainHandlers: function () {
      var self = this;

      // Open/close Pontoon UI
      $('#switch').unbind("click.pontoon").bind("click.pontoon", function () {
        if ($(this).is('.opened')) {
          $('#sidebar').hide();
          $('#source, #iframe-cover').css('margin-left', 0);
          self.common.postMessage("MODE", "Advanced");
        } else {
          $('#sidebar').show();
          $('#source, #iframe-cover').css('margin-left', $('#sidebar').width());
          self.common.postMessage("MODE", "Basic");
        }
        $('#source, #iframe-cover').width($(window).width() - $('#sidebar:visible').width());
        self.common.postMessage("RESIZE");
        $(this).toggleClass('opened');
      });

      // Profile menu
      $('#profile-menu').find('a').click(function (e) {
        e.preventDefault();
        if ($(this).is(".sign-out")) {
          window.location = 'signout/'; // Without this, Enter doesn't open the link
        } else if ($(this).is(".admin")) {
          window.location = $(this).attr('href'); // Without this, Enter doesn't open the link
        } else if ($(this).is(".html")) {
          self.common.postMessage("HTML");
        } else {
          self.save($(this).attr('class').split(" ")[0]);
        }
      });

      // Transifex and SVN authentication
      $('.popup').find('.cancel').click(function (e) {
        e.preventDefault();
        $('.popup').hide();
      }).end().find('.button').click(function (e) {
        e.preventDefault();
        var type = $(this).parents('.popup').attr('id');
        self.save(type, $('#' + type + ' form').serializeArray());
      });
    },



    /*
     * Create user interface
     */
    createUI: function () {
      var self = this;

      self.attachMainHandlers();
      self.renderEntityList();
      self.updateProgress();
      self.attachEditorHandlers();

      $("#spinner").fadeOut(function() {
        $("#pontoon > header > .container").fadeIn();
      });

      // If advanced features opened by default, open first entity in the editor
      if (!self.project.win || self.project.width) {
        $("#entitylist .entity:first").mouseover().click();
      }
    },


    /*
     * Handle messages from project code
     */
    receiveMessage: function (e) {
      if (e.source === Pontoon.project.win) {
        var message = JSON.parse(e.data);

        switch (message.type) {

        case "DATA":
          // Deep copy: http://api.jquery.com/jQuery.extend
          Pontoon.project.entities = $.extend(
            true,
            Pontoon.project.entities,
            message.value.entities);
          break;

        case "RENDER":
          var value = message.value;
          Pontoon.project.url = value.url;
          Pontoon.project.title = value.title;
          Pontoon.createUI();
          break;

        case "ERROR":
          var msg = message.value ||
              'Oops, something went wrong. Refresh to try again.';
          Pontoon.common.showError(msg);
          $("#progress, #switch, #drag").remove();
          $("#spinner").fadeOut(function() {
            $("#pontoon > header > .container").fadeIn();
          });
          Pontoon.attachMainHandlers();
          break;

        case "SWITCH":
          $("#switch").click();
          break;

        case "HOVER":
          Pontoon.project.entities[message.value].ui.addClass('hovered');
          break;

        case "UNHOVER":
          Pontoon.project.entities[message.value].ui.removeClass('hovered');
          break;

        case "ACTIVE":
          if ($('#switch').is('.opened')) {
            var entity = Pontoon.project.entities[message.value];
            Pontoon.openEditor(entity);
          }
          break;

        case "INACTIVE":
          if (!Pontoon.project.width && $("#editor").is('.opened')) {
            $('#cancel').click();
          }
          break;

        case "UPDATE":
          var entity = Pontoon.project.entities[message.value.id];
          Pontoon.updateOnServer(entity, message.value.content);
          break;

        case "DELETE":
          var entity = Pontoon.project.entities[message.value];
          Pontoon.updateEntityUI(entity);
          break;

        case "HTML":
          Pontoon.save("html", message.value);
          break;

        }
      }
    },



    /*
     * Initialize Pontoon
     *
     * app Pontoon window object
     * project Website window object
     */
    init: function (app, project) {
      var self = this;

      // Build Pontoon object
      this.app = {
        win: app,
        path: $('base').attr('href') // pontoon.css injection
      };
      this.project = {
        win: project,
        url: "",
        title: "",
        entities: $('#server').data('entities') || [],
        pk: $('#server').data('id'),
        format: $('#server').data('format'),
        width: (
          $('#server').data('width') &&
          ($(window).width() - $('#server').data('width')) >= 900) ?
          $('#server').data('width') : false,
        links: $('#server').data('links')
      };
      this.locale = {
        code: $('#server').data('locale'),
        language: $("#pontoon > header .language").contents()[0].nodeValue
      };
      this.user = {
        email: $('#server').data('email') || '',
        name: $('#server').data('name') || '',
        localizer: $('#server').data('localizer'),
        manager: $('#server').data('manager')
      };

      // Initialize Pontoon for projects with in-place translation support
      // (iframe cross-domain policy solution)
      if (project) {
        self.common.postMessage("INITIALIZE", {
          path: self.app.path,
          links: self.project.links,
          entities: self.project.entities,
          pk: self.project.pk,
          format: self.project.format,
          locale: self.locale,
          user: self.user
        });

        // Wait for project code messages
        window.addEventListener("message", self.receiveMessage, false);

      // Initialize Pontoon for projects without in-place translation support
      } else {
        $(self.project.entities).each(function (i) {
          this.id = i;
        });
        self.createUI();
      }
    },



    /*
     * Update slider position in the menu
     * 
     * menu Menu element
     */
    updateSlider: function (menu) {
      var hovered = menu.find('li.hover'),
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
     * Common functions used in both, client specific code and Pontoon library
     */
    common: (function () {
      // Show/hide menu on click
      $('.selector').click(function (e) {
        if (!$(this).siblings('.menu').is(':visible')) {
          e.stopPropagation();
          $('body:not(".admin-form") .menu, body:not(".admin-form") .popup').hide();
          $('.select').removeClass('opened');
          $('#iframe-cover').hide(); // iframe fix
          $(this).siblings('.menu').show().end()
                 .parents('.select').addClass('opened');
          $('#iframe-cover').show(); // iframe fix
          $('.search:visible').focus();
        }
      });

      // Hide menus on click outside
      $('body:not(".admin-form")').click(function () {
        $('.menu').hide();
        $('#iframe-cover').hide(); // iframe fix
        $('.select').removeClass('opened');
      });

      // Menu hover
      $('.menu li').live('hover', function () {
        $('.menu li.hover').removeClass('hover');
        $(this).toggleClass('hover');
      });

      // Show only pages available for the selected project
      $('.page .selector').click(function () {
        var pages = Pontoon.common.getProjectResources('pages'),
            menu = $(this).siblings('.menu').find('ul');

        if (pages) {
          menu.find('li:not(".no-match")').remove();
          $(pages.reverse()).each(function() {
            menu.prepend('<li>' + this + '</li>');
          });
        }

        $('.search:visible').trigger("keyup");
      });

      // Show only locales available for the selected project
      $('.locale .selector').click(function () {
        var locales = Pontoon.common.getProjectResources('locales'),
            menu = $(this).siblings('.menu');

        menu.find('.limited').removeClass('limited');
        if (locales) {
          menu.find('li').hide();
          $(locales).each(function() {
            menu.find('.language.' + this).parent().addClass('limited').show();
          });
        }

        $('.search:visible').trigger("keyup");
      });

      // Open selected project (page) and locale combination
      $('#go').click(function (e) {
        e.preventDefault();
        e.stopPropagation();

        var locale = $('.locale .selector .language').attr('class').split(' ')[1],
            project = $('.project .selector .title').html(),
            page = $('.page .selector .title:visible').html(),
            loc = '/locale/' + locale + '/project/' + project;

        // On homepage, show error if no project selected
        if (!locale) {
          Pontoon.common.showError("Oops, no project selected.");
          return;
        }

        if (page) {
          loc += '/page/' + page;
        }
        window.location = loc;
      });

      // Project menu handler
      $('.project .menu li:not(".no-match")').click(function () {
        var name = $(this).find('.project-name').html(),
            url = $(this).find('.project-url').html();

        $('.project .selector .title')
          .html(name)
          .data('url', url);

        if ($('body').is('.admin')) {
          return false;
        }

        // Fallback if selected page not available for the selected project
        var defaultPage = Pontoon.common.getProjectResources('pages')[0];
        if (defaultPage) {
          $('.page .selector .title').html(defaultPage);
          $('header .page').removeClass("hidden").find('.selector .title').html(defaultPage);
        } else {
          $('header .page').addClass("hidden");
        }

        // Fallback if selected locale not available for the selected project
        var locales = Pontoon.common.getProjectResources('locales'),
            menu = $('.locale .menu'),
            selector = menu.siblings('.selector'),
            selected = selector.find('.code').html();

        if (locales.indexOf(selected) === -1) {
          var defaultLocale = menu.find('.language.' + locales[0])[0].outerHTML;
          selector.html(defaultLocale);
        }
      });

      // Page menu handler
      $('.page .menu li:not(".no-match")').live("click.pontoon", function () {
        var title = $(this).html();
        $('.page .selector .title').html(title);
      });

      // Locale menu handler
      $('body:not(".admin-form") .locale .menu li:not(".no-match")').click(function () {
        var locale = $(this).find('.language').attr('class').split(' ')[1],
            locale = locale.replace( /(:|\.|\[|@|\])/g, "\\$1" ), // Escape special characters in CSS notation
            language = $('.locale .menu .language.' + locale).html();

        $('.locale .selector .language')
          .attr('class', 'language ' + locale)
          .html(language);
      });

      // Add case insensitive :contains-like selector to jQuery (needed for locale search)
      $.expr[':'].containsi = function(a, i, m) {
        return (a.textContent || a.innerText || '').toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
      };

      // Project, page and locale search
      $('.search').click(function (e) {
        e.stopPropagation();
      }).keyup(function(e) {
        var ul = $(this).siblings('ul'),
            val = $(this).val(),
            // Only search a limited set if defined
            limited = ul.find('li.limited').length > 0 ? '.limited' : '';

        ul
          .find('li' + limited).show().end()
          .find('li' + limited + ':not(":containsi("' + val + '")")').hide();

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
            if (menu.parent().is('.locale')) {
              Pontoon.updateSlider(menu.find('ul'));
            }
            if (menu.parent().is('.project')) {
              var type = (!$('body').is('.admin')) ? '.project-url' : '.project-name';
              $('.url').val($('.project .menu li.hover').find(type).html());
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
              var type = (!$('body').is('.admin')) ? '.project-url' : '.project-name';
              $('.url').val($('.project .menu li.hover').find(type).html());
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
         * Get resources available for selected project
         *
         * resourceType locales or pages
         */
        getProjectResources: function(resourceType) {
          var resources = null;

          $('.project-name').each(function() {
            if ($('.project .button .title').html() === $(this).html()) {
              resources = $(this).data(resourceType).split(',');
              resources.pop();
              return false;
            }
          });

          return resources;
        },
        /*
         * Show error message
         *
         * message Error message to be displayed
         */
        showError: function(message) {
          $('.notification')
            .html('<li>' + message + '</li>')
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
          if (!Pontoon.project.win) {
            return false;
          }
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
