/* Extend public object */
var Pontoon = (function (my) {
  return $.extend(true, my, {

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
            locale: this.locale.code,
            project: this.project.pk
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
          action: '/download/'
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
        var entities = strip(this.entities);
        params.content = JSON.stringify(entities, null, "\t");
        download(params);

      } else if (type === "zip") {
        download(params);
      }
    },


    getOtherLocales: function (entity) {
      var self = this,
          list = $('#other-locales ul').empty(),
          tab = $('#helpers a[href="#other-locales"]').addClass('loading');

      if (self.XHRgetOtherLocales) {
        self.XHRgetOtherLocales.abort();
      }

      self.XHRgetOtherLocales = $.ajax({
        url: '/other-locales/',
        data: {
          entity: entity.pk,
          locale: self.locale.code
        },
        success: function(data) {
          if (data !== "error") {
            $.each(data, function() {
              list.append('<li title="Click to copy">' +
                '<header>' + this.locale.name + '<span class="stress">' + this.locale.code + '</span></header>' +
                '<p class="translation" dir="auto" lang="' + this.locale.code + '">' +
                  self.doNotRender(this.translation) +
                '</p>' +
              '</li>');
            });
          } else {
            list.append('<li class="disabled"><p>No translations available.</p></li>');
          }
          tab.removeClass('loading');
        },
        error: function(error) {
          if (error.status === 0 && error.statusText !== "abort") {
            // Allows requesting locales again
            editor.otherLocales = null;
            self.noConnectionError(list);
            tab.removeClass('loading');
          }
        }
      });
    },


    /*
     * Get currently selected plural form
     *
     * normalize If true, return 0 instead of -1 for non-pluralized entities
     */
    getPluralForm: function (normalize) {
      var pluralForm = $('#plural-tabs li.active:visible').index();
      if (normalize && pluralForm === -1) {
        pluralForm = 0;
      }
      return pluralForm;
    },


    /*
     * Get history of translations of given entity
     *
     * entity Entity
     */
    getHistory: function (entity) {
      var self = this,
          list = $('#history ul').empty(),
          tab = $('#helpers a[href="#history"]').addClass('loading');

      if (self.XHRgetHistory) {
        self.XHRgetHistory.abort();
      }

      self.XHRgetHistory = $.ajax({
        url: '/get-history/',
        data: {
          entity: entity.pk,
          locale: self.locale.code,
          plural_form: self.getPluralForm()
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
                      ((self.user.email === this.email && !this.approved) ?
                        ' own' : '')) +
                    '">' +
                    '<div class="info">' +
                      ((!this.email) ? this.user :
                        '<a href="/contributors/' + this.email + '">' + this.user + '</a>') +
                      '<time class="stress" datetime="' + this.date_iso + '">' + this.date + '</time>' +
                    '</div>' +
                    '<menu class="toolbar">' +
                      '<button class="approve fa" title="' +
                      (this.approved ? this.approved_user ?
                        'Approved by ' + this.approved_user : '' : 'Approve') +
                      '"></button>' +
                      '<button class="delete fa" title="Delete"></button>' +
                    '</menu>' +
                  '</header>' +
                  '<p class="translation" dir="auto" lang="' + self.locale.code + '">' +
                    self.doNotRender(this.translation) +
                  '</p>' +
                '</li>');
            });
            $("#history time").timeago();
          } else {
            list.append('<li class="disabled"><p>No translations available.</p></li>');
          }
          tab.removeClass('loading');
        },
        error: function(error) {
          if (error.status === 0 && error.statusText !== "abort") {
            self.noConnectionError(list);
            tab.removeClass('loading');
          }
        }
      });
    },


    /*
     * Open translation editor in the main UI
     *
     * entity Entity
     * inplace Was editor opened from in place?
     */
    openEditor: function (entity, inplace) {
      $("#editor")[0].entity = entity;

      // Metadata: comments, sources, keys
      $('#metadata').empty().hide();
      if (entity.comment) {
        $('#metadata').html('<span id="comment">' + this.doNotRender(entity.comment) + '</span>').show();
      }
      if (entity.source || entity.path || entity.key) {
        $('#metadata').append('<a href="#" class="details">More details</a>').show();
      }
      if (entity.source) {
        if (typeof(entity.source) === 'object') {
          $.each(entity.source, function() {
            $('#metadata').append('<span>#: ' + this.join(':') + '</span>');
          });
        } else {
          $('#metadata').append('<span>' + entity.source + '</span>');
        }
      }
      if (entity.path) {
        $('#metadata').append('<span>' + entity.path + '</span>');
      }
      if (entity.key && entity.key != entity.original) {
        $('#metadata').append('<span>Key: ' + entity.key + '</span>');
      }

      // Translation area (must be set before unsaved changes check)
      $('#translation').val(entity.translation[0].string);
      $('.warning-overlay:visible .cancel').click();

      // Original string and plurals
      $('#original').html(entity.marked);
      $('#source-pane').removeClass('pluralized');
      $('#plural-tabs li').css('display', 'none');

      if (entity.original_plural) {
        $('#source-pane').addClass('pluralized');

        var nplurals = this.locale.nplurals;
        if (nplurals > 1) {

          // Get example number for each plural form based on locale plural rule
          if (!this.locale.examples) {
            var CLDR_PLURALS = ['zero', 'one', 'two', 'few', 'many', 'other'],
                examples = this.locale.examples = {},
                n = 0;

            if (nplurals === 2) {
              examples = {0: 1, 1: 2};

            } else {
              while (Object.keys(examples).length < nplurals) {
                var rule = eval(this.locale.plural_rule);
                if (!examples[rule]) {
                  examples[rule] = n;
                }
                n++;
              }
            }

            $.each(this.locale.cldr_plurals, function(i) {
              $('#plural-tabs li:eq(' + i + ') a')
                .find('span').html(CLDR_PLURALS[this]).end()
                .find('sup').html(examples[i]);
            });
          }
          $('#plural-tabs li:lt(' + nplurals + ')').css('display', 'table-cell');
          $('#plural-tabs li:first a').click();
        }
      }
      $("#helpers nav .active a").click();

      // Focus
      if (!inplace) {
        $('#translation').focus();
      }

      // Length
      var original = entity['original' + this.isPluralized()].length,
          translationString = entity.translation[0].string,
          translation = translationString ? translationString.length : 0;

      $('#translation-length')
        .show() // Needed if sidebar opened by default
        .find('.original-length').html(original).end()
        .find('.current-length').html(translation);

      // Update entity list
      $("#entitylist .hovered").removeClass('hovered');
      entity.ui.addClass('hovered');
      this.updateScroll($('#entitylist .wrapper'));

      // Switch editor and entitylist in 1-column layout
      if (!this.app.advanced) {
        $("#entitylist")
          .css('left', -$('#sidebar').width()/2);

        $("#editor").addClass('opened').css('left', 0);
      }
    },


    /*
     * Get entity status: 'translated', 'approved', 'fuzzy', ''
     *
     * entity Entity
     */
    getEntityStatus: function (entity) {
      var translation = entity.translation,
          approved = translated = fuzzy = 0;

      for (i=0; i<translation.length; i++) {
        if (entity.translation[i].approved) {
          approved++;
        }
        if (entity.translation[i].fuzzy) {
          fuzzy++;
        }
        // Include empty and anonymous translations
        if (entity.translation[i].pk || entity.translation[i].string) {
          translated++;
        }
      }

      if (i === approved) {
        return 'approved';
      } else if (i === fuzzy) {
        return 'fuzzy';
      } else if (i === translated) {
        return 'translated';
      }
      return '';
    },


    /*
     * Check unsaved changes in editor
     *
     * callback Callback function
     */
    checkUnsavedChanges: function (callback) {
      var entity = $('#editor')[0].entity;

      // Ignore for anonymous users, for which we don't save traslations
      if (!this.user.email || !entity) {
        return callback();
      }

      var pluralForm = this.getPluralForm(true),
          translation = entity.translation[pluralForm].string,
          source = $('#translation').val();

      if ((translation !== null) && (translation !== source)) {
        $('#unsaved').show();
        $("#translation").focus();
        this.checkUnsavedChangesCallback = callback;

      } else {
        return callback();
      }
    },


    /*
     * Switch to new entity in editor
     *
     * newEntity New entity we want to switch to
     */
    switchToEntity: function (newEntity) {
      var self = this;

      self.checkUnsavedChanges(function() {
        var oldEntity = $('#editor')[0].entity;

        if (newEntity.body || (oldEntity && oldEntity.body)) {
          self.postMessage("NAVIGATE", newEntity.id);
        }
        if (!newEntity.body) {
          self.openEditor(newEntity);
        }
      });
    },


    /*
     * Render list of entities to translate
     */
    renderEntityList: function () {
      var self = this,
          list = $('#entitylist');

      // Trigger event with a delay (e.g. to prevent UI blocking)
      var delay = (function () {
        var timer = 0;
        return function (callback, ms) {
          clearTimeout(timer);
          timer = setTimeout(callback, ms);
        };
      })();

      function searchEntities() {
        var ul = $('#entitylist .wrapper > ul'),
            val = $('#search').val();

        ul
          .find('.limited').show()
            .find('.string-wrapper' + ':not(":containsi(\'' + val + '\')")')
          .parent().hide();

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
      }

      // Search entities
      $('#search').keyup(function (e) {
        delay(function () {
          searchEntities();
        }, 200);
      });

      // Filter entities
      $('#filter li:not(".horizontal-separator")').click(function() {
        var list = $("#entitylist"),
            type = $(this).attr('class').split(' ')[0];

        list.find('.entity').addClass('limited').show();

        switch (type) {

        case "untranslated":
          list.find('.entity.approved, .entity.translated, .entity.fuzzy')
            .removeClass('limited').hide();
          break;

        case "fuzzy":
          list.find('.entity:not(".fuzzy")')
            .removeClass('limited').hide();
          break;

        case "translated":
          list.find('.entity:not(".translated")')
            .removeClass('limited').hide();
          break;

        case "approved":
          list.find('.entity:not(".approved")')
            .removeClass('limited').hide();
          break;

        case "unchanged":
          list.find('.entity').each(function() {
            var entity = this.entity;
            if (entity.original !== entity.translation[0].string) {
              $(this).removeClass('limited').hide();
            }
          });
          break;

        }

        searchEntities();
        $('#filter .title').html($(this).text());
        $('#filter .button').attr('class', 'button selector ' + type);
      });

      // Render
      $(self.entities).each(function () {
        var status = self.getEntityStatus(this),
            li = $('<li class="entity limited' +
          (status ? ' ' + status : '') +
          (!this.body ? ' uneditable' : '') + '">' +
          '<span class="status fa"></span>' +
          '<p class="string-wrapper">' +
            '<span class="source-string">' + this.marked + '</span>' +
            '<span class="translation-string" dir="auto" lang="' + self.locale.code + '">' +
              self.doNotRender(this.translation[0].string || '') +
            '</span>' +
          '</p>' +
          '<span class="arrow fa fa-chevron-right fa-lg"></span>' +
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
        self.postMessage("HOVER", this.entity.id);
      }, function () {
        self.postMessage("UNHOVER", this.entity.id);
      });

      // Open entity editor on click
      $("#entitylist .entity").click(function () {
        self.switchToEntity(this.entity);
      });
    },


    /*
     * Is original string pluralized
     */
    isPluralized: function () {
      var original = '',
          nplurals = this.locale.nplurals,
          plural_rule = this.locale.plural_rule,
          pluralForm = this.getPluralForm();

      if ((nplurals === 2 && pluralForm === 1) ||
          (nplurals > 2 &&
           pluralForm !== -1 &&
           pluralForm !== eval(plural_rule.replace(/n/g, 1)))) {
        original = '_plural';
      }

      return original;
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
            entitySelector = '#entitylist .entity:visible',
            index = $('#editor')[0].entity.ui.index(entitySelector);

        switch (sec) {

        case "back":
          self.checkUnsavedChanges(function() {
            $('#cancel').click();
          });
          break;

        case "previous":
          var prev = $(entitySelector).eq(index - 1);
          if (prev.length === 0) {
            prev = $(entitySelector + ':last');
          }
          self.switchToEntity(prev[0].entity);
          break;

        case "next":
          var next = $(entitySelector).eq(index + 1);
          if (next.length === 0) {
            next = $(entitySelector + ':first');
          }
          self.switchToEntity(next[0].entity);
          break;

        }
      });

      // Show/hide more source string metadata
      $("#metadata").on("click", "a.details", function (e) {
        e.stopPropagation();
        e.preventDefault();

        var details = $("#metadata span:not('#comment')");
        if ($(this).is(':contains("Less")')) {
          $(this).html('More details');
          details.css('display', 'none');
        } else {
          $(this).html('Less details');
          details.css('display', 'block');
        }
      });

      // Insert placeable at cursor or at the end if not focused
      $("#original").on("click", ".placeable", function (e) {
        e.stopPropagation();
        e.preventDefault();

        var textarea = $('#translation'),
            pos = textarea[0].selectionStart,
            placeable = $(this).text(),
            before = textarea.val(),
            after = before.substring(0, pos) + placeable + before.substring(pos);

        textarea.val(after).focus();
      });

      function switchToPluralForm(tab) {
        $("#plural-tabs li").removeClass('active');
        tab.addClass('active');

        var entity = $('#editor')[0].entity,
            i = tab.index(),
            original = entity['original' + self.isPluralized()],
            marked = entity['marked' + self.isPluralized()],
            title = !self.isPluralized() ? "Singular" : "Plural",
            source = entity.translation[i].string;

        $('#source-pane h2').html(title).show();
        $('#original').html(marked);

        $('#translation').val(source).focus();
        $('#translation-length')
          .find('.original-length').html(original.length).end()
          .find('.current-length').html($('#translation').val().length);

        $('#quality:visible .cancel').click();
        $("#helpers nav .active a").click();
      }

      // Plurals navigation
      $("#plural-tabs a").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var tab = $(this).parent();

        // Only if actually clicked on tab
        if (e.hasOwnProperty('originalEvent')) {
          self.checkUnsavedChanges(function() {
            switchToPluralForm(tab);
          });
        } else {
          switchToPluralForm(tab);
        }
      });

      // Translate textarea keyboard shortcuts
      $('#translation').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
        var key = e.which;

        // Prevent triggering unnecessary events in 1-column layout
        if (!$("#editor").is('.opened')) {
          return false;
        }

        // Enter: save translation
        if (key === 13 && !e.shiftKey && !e.altKey) {
          if ($('#leave-anyway').is(':visible')) {
            $('#leave-anyway').click();
          } else {
            $('#save').click();
          }
          return false;
        }

        // Esc: cancel translation and return to entity list
        if (key === 27) {
          if ($('.warning-overlay').is(':visible')) {
            $('.warning-overlay .cancel').click();
          } else if (!self.app.advanced) {
            $('#cancel').click();
          }
          return false;
        }

        // Alt + C: copy from source
        if (e.altKey && key === 67) {
          $('#copy').click();
          return false;
        }

        // Alt + Backspace: clear translation
        if (e.altKey && key === 8) {
          $('#clear').click();
          return false;
        }

        // Alt + Down: go to next string
        if (e.altKey && key === 40) {
          $('#next').click();
          return false;
        }

        // Alt + Up: go to previous string
        if (e.altKey && key === 38) {
          $('#previous').click();
          return false;
        }

        // Tab: select suggestions
        if (!$('.menu').is(':visible') && !$('.popup').is(':visible') && key === 9) {

          var section = $('#helpers section:visible'),
              index = section.find('li.hover').index() + 1;

          // If possible, select next suggestion, or select first
          if (section.find('li:last').is('.hover')) {
            index = 0;
          }

          section
            .find('li').removeClass('hover').end()
            .find('li:eq(' + index + ')').addClass('hover').click();

          self.updateScroll(section);
          return false;
        }

      // Update length (keydown is triggered too early)
      }).unbind("input propertychange").bind("input propertychange", function (e) {
        var length = $('#translation').val().length;
        $('#translation-length .current-length').html(length);

        $('.warning-overlay:visible .cancel').click();
      });

      // Close warning box
      $('.warning-overlay .cancel').click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        $('.warning-overlay')
          .find('ul').empty().end()
        .hide();

        $('#translation').focus();
      });

      $('#leave-anyway').click(function() {
        var callback = self.checkUnsavedChangesCallback;
        if (callback) {
          callback();
          $('#unsaved').hide();
        }
      });

      // Copy source to translation
      $("#copy").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $('#editor')[0].entity,
            original = entity['original' + self.isPluralized()],
            source = original;

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
      $('#cancel').click(function (e, data) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $("#editor")[0].entity,
            data = data || {};

        $("#entitylist")
          .css('left', 0)
          .find('.hovered').removeClass('hovered');

        $("#editor")
          .removeClass('opened')
          .css('left', $('#sidebar').width());

        // Only if editable and not already handled inplace
        if (entity.body && !data.inplace) {
          self.postMessage("CANCEL");
          self.postMessage("UNHOVER", entity.id);
        }
      });

      // Save translation
      $('#save, #save-anyway').click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $('#editor')[0].entity,
            source = $('#translation').val();

        if (source === '' &&
          ['properties', 'ini', 'dtd'].indexOf(entity.format) === -1) {
            self.endLoader('Empty translations cannot be submitted.', 'error');
            return;
        }

        self.updateOnServer(entity, source, false, true);
      });

      // Helpers navigation
      $("#helpers nav a").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        $("#helpers nav li").removeClass('active');
        $(this).parent().addClass('active');

        var sec = $(this).attr('href').substr(1),
            editor = $('#editor')[0],
            entity = editor.entity,
            currentEntity = entity.id,
            currentEntityPlural = currentEntity + self.isPluralized();

        switch (sec) {

        case "history":
          // Do not cache history to prevent outdated suggestions on return
          self.getHistory(entity);
          break;

        case "machinery":
          if (editor.machinery !== currentEntityPlural) {
            self.getMachinery(entity['original' + self.isPluralized()]);
            editor.machinery = currentEntityPlural;
          }
          break;

        case "other-locales":
          if (editor.otherLocales !== currentEntity) {
            // Hard to match plural forms with other locales; using singular
            self.getOtherLocales(entity);
            editor.otherLocales = currentEntity;
          }
          break;

        }

        $("#helpers > section").hide();
        $("#helpers > section#" + sec).show();

        // Only if actually clicked on tab
        if (e.hasOwnProperty('originalEvent')) {
          $("#custom-search input[type=search]:visible").focus();
        }
      });

      // Custom search: trigger with Enter
      $('#custom-search input').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
        var value = $(this).val();
        if (e.which === 13 && value.length > 0) {
          self.getMachinery(value, "custom-search");
          return false;
        }
      });

      // Copy helpers result to translation
      $("#helpers section").on("click", "li:not('.disabled')", function (e) {
        e.stopPropagation();
        e.preventDefault();

        var translation = $(this).find('.translation').text(),
            source = translation;
        $('#translation').val(source).focus();
        $('#translation-length .current-length').html(source.length);

        $('.warning-overlay:visible .cancel').click();
      });

      // Restore clickable links
      $("#helpers section").on("click", "li a", function (e) {
        e.stopPropagation();
      });

      // Approve and delete translations
      $("#history").on("click", "menu button", function (e) {
        var button = $(this);
        if (button.is('.approve') && button.parents('li.approved').length > 0) {
          return;
        }

        e.stopPropagation();
        e.preventDefault();

        if (button.is('.approve')) {
          button
            .parents('li').addClass('approved').click()
              .siblings().removeClass('approved');

          $('#save').click();
          return;
        }

        $.ajax({
          url: '/delete-translation/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            translation: $(this).parents('li').data('id')
          },
          success: function(data) {
            if (data.type === "deleted") {
              var item = button.parents('li'),
                  index = item.index();
              item
                .addClass('delete')
                .bind('transitionend', function() {
                  $(this).remove();
                  self.endLoader('Translation deleted');

                  // Active translation deleted
                  if (index === 0) {
                    var entity = $('#editor')[0].entity,
                        next = $('#history li[data-id="' + data.next + '"]'),
                        pluralForm = self.getPluralForm(true);

                    // Make newest alternative translation active
                    if (next.length > 0) {
                      next.click();
                      translation = next.find('.translation').text();
                      entity.translation[pluralForm].string = translation;
                      entity.ui.find('.translation-string')
                        .html(self.doNotRender(translation));
                      if (self.user.localizer) {
                        next.addClass('approved');
                        if (entity.body) {
                          self.postMessage("SAVE", entity.translation[0].string);
                        }
                      }

                    // Last translation deleted, no alternative available
                    } else {
                      $('#translation').val('').focus();
                      if (entity.body && pluralForm === 0) {
                        self.postMessage("DELETE");
                      } else {
                        entity.translation[pluralForm].pk = null;
                        entity.translation[pluralForm].string = null;
                        entity.translation[pluralForm].approved = false;
                        entity.translation[pluralForm].fuzzy = false;
                        self.updateEntityUI(entity);
                      }
                      $('#history ul')
                        .append('<li class="disabled">' +
                                  '<p>No translations available.</p>' +
                                '</li>');
                    }
                  }
                });
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
          approved = $("#entitylist .entity.approved").length,
          translated = $("#entitylist .entity.translated").length,
          fuzzy = $("#entitylist .entity.fuzzy").length,
          untranslated = all - translated - approved - fuzzy,
          fraction = {
            approved: all ? approved / all : 0,
            translated: all ? translated / all : 0,
            fuzzy: all ? fuzzy / all : 0,
            untranslated: all ? untranslated / all : 0
          },
          number = Math.floor(fraction.approved * 100);

      // Update graph
      $('#progress .graph').each(function() {
        var context = this.getContext('2d');
        context.lineWidth = this.width/11;

        var x = this.width/2,
            y = this.height/2,
            radius = (this.width - context.lineWidth)/2,
            end = null;

        $('#progress .details > div').each(function(i) {
          var type = $(this).attr('class'),
              length = fraction[type] * 2,
              start = (end !== null) ? end : -0.5;
          end = start + length;

          context.beginPath();
          context.arc(x, y, radius, start * Math.PI, end * Math.PI);
          context.strokeStyle = $(this).css("border-top-color");
          context.stroke();
        });
      });

      // Update number
      $('#progress .number').html(number);

      // Update details in the menu
      $('#progress .menu').find('header span').html(all).end()
        .find('.details')
          .find('.approved p').html(approved).end()
          .find('.translated p').html(translated).end()
          .find('.fuzzy p').html(fuzzy).end()
          .find('.untranslated p').html(untranslated);

      // Update parts menu
      if (all) {
        var details = Pontoon.getProjectDetails(),
            path = this.entities[0].path;

        $(details[this.locale.code.toLowerCase()]).each(function() {
          if (this.resource__path === path) {
            this.approved_count = approved;
            this.translated_count = translated;
          }
        });
      }
    },


    /*
     * Update entity in the entity list
     *
     * entity Entity
     */
    updateEntityUI: function (entity) {
      entity.ui.removeClass('translated approved fuzzy');

      var status = this.getEntityStatus(entity),
          translation = entity.translation[0].string;
      entity.ui.addClass(status);
      entity.ui.find('.translation-string')
        .html(this.doNotRender(translation || ''));

      this.updateProgress();
    },


    /*
     * Update all translations in localStorage on server
     */
    syncLocalStorageOnServer: function() {
      if (localStorage.length !== 0) {
        var len = this.entities.length;
        for (var i = 0; i < len; i++) {
          var entity = this.entities[i],
              key = this.getLocalStorageKey(entity),
              value = localStorage[key];
          if (value) {
            value = JSON.parse(localStorage[key]);
            this.updateOnServer(entity, value.translation, false, false);
            delete localStorage[key];
          }
        }
        // Clear all other translations
        localStorage.clear();
      }
    },


    /*
     * Generate localStorage key
     *
     * entity Entity
     */
    getLocalStorageKey: function(entity) {
      return this.locale.code + "/" + entity.pk;
    },


    /*
     * Add entity translation to localStorage
     *
     * entity Entity
     * translation Translation
     */
    addToLocalStorage: function(entity, translation) {
      localStorage.setItem(this.getLocalStorageKey(entity), JSON.stringify({
        translation: translation,
      }));
    },


    /*
     * Show quality check warnings
     *
     * warnings Array of warnings
     */
    showQualityCheckWarnings: function(warnings) {
      $('#quality ul').empty();
      $(warnings).each(function() {
        $('#quality ul').append('<li>' + this + '</li>');
      });
      $('#quality').show();
    },


    /*
     * Update entity translation on server
     *
     * entity Entity
     * translation Translation
     * inplace Was translation submitted in place?
     * syncLocalStorage Synchronize translations in localStorage with the server
     */
    updateOnServer: function (entity, translation, inplace, syncLocalStorage) {
      var self = this,
          pluralForm = self.getPluralForm();

      self.startLoader();

      function gotoEntityListOrNextEntity() {
        // Go to entity list
        if (!self.app.advanced && $("#editor").is('.opened')) {
          $('#cancel').trigger('click', [{inplace: inplace}]);

        // Go to next entity
        } else {
          $('#next').click();
        }
      }

      function renderTranslation(data) {
        if (data.type) {
          self.endLoader('Translation ' + data.type);

          var pf = self.getPluralForm(true);
          entity.translation[pf] = data.translation;
          self.updateEntityUI(entity);

          // Update translation, including in place if possible
          if (!inplace && entity.body && (self.user.localizer ||
              !entity.translation[pf].approved)) {
            self.postMessage("SAVE", {
              translation: translation,
              id: entity.id
            });
          }

          // Quit
          if (!$("#editor:visible").is('.opened')) {
            return;

          // Go to next plural form
          } else if (pluralForm !== -1 && $("#editor").is('.opened')) {
            var next = $('#plural-tabs li:visible')
              .eq(pluralForm + 1).find('a');

            if (next.length === 0) {
              gotoEntityListOrNextEntity();
            } else {
              next.click();
            }

          // Go to entity list or next entity
          } else {
            gotoEntityListOrNextEntity();
          }

        } else if (data.warnings) {
          self.endLoader();
          self.showQualityCheckWarnings(data.warnings);

        } else if (data === "error") {
          self.endLoader('Oops, something went wrong.', 'error');

        } else {
          self.endLoader(data, 'error');
        }
      }

      $.ajax({
        url: '/update/',
        type: 'POST',
        data: {
          csrfmiddlewaretoken: $('#server').data('csrf'),
          locale: self.locale.code,
          entity: entity.pk,
          translation: translation,
          plural_form: pluralForm,
          original: entity['original' + self.isPluralized()],
          ignore_check: inplace || $('#quality').is(':visible') || !syncLocalStorage
        },
        success: function(data) {
          renderTranslation(data);
          // Connection exists -> sync localStorage
          if (syncLocalStorage) {
            self.syncLocalStorageOnServer();
          }
        },
        error: function(error) {
          if (error.status === 0) {
            // No connection -> use offline mode
            self.addToLocalStorage(entity, translation);
            // Imitate data to add translation
            var data = {
              type: "added",
              translation: {
                approved: self.user.localizer,
                fuzzy: false,
                string: translation
              }
            };
            renderTranslation(data);
          } else {
            self.endLoader('Oops, something went wrong.', 'error');
          }
        }
      });
    },


    /*
     * Attach event handlers to main toolbar elements
     */
    attachMainHandlers: function () {
      var self = this;

      // Hide menus on click outside
      $('body').bind("click.main", function (e) {
        $('.menu, #hotkeys').hide();
        $('#iframe-cover').hide(); // iframe fix
        $('.select').removeClass('opened');
        $('.menu li').removeClass('hover');

        // Special case: menu in menu
        if ($(e.target).is('.hotkeys') || $(e.target).parent().is('.hotkeys')) {
          $('#hotkeys').show();
          $('#iframe-cover').show(); // iframe fix
        }
      });

      // Open/close sidebar
      $('#switch').unbind("click.pontoon").bind("click.pontoon", function () {
        if ($(this).is('.opened')) {
          $('#sidebar').hide();
          $('#source, #iframe-cover').css('margin-left', 0);
          self.postMessage("MODE", "Advanced");
        } else {
          $('#sidebar').show();
          $('#source, #iframe-cover').css('margin-left', $('#sidebar').width());
          self.postMessage("MODE", "Basic");
        }
        $('#source, #iframe-cover').width($(window).width() - $('#sidebar:visible').width());
        self.postMessage("RESIZE");
        $(this).toggleClass('opened');
      });

      // Project menu handler
      $('.project .menu li:not(".no-match")').click(function () {
        var project = $(this).find('.name'),
            name = project.html(),
            slug = project.data('slug');

        if (slug !== 'pontoon-intro' && !self.user.email) {
          return self.endLoader('Sign in to access more projects.', 'error', true);
        }

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
          menu.find('.code').each(function() {
            var code = $(this).html().toLowerCase();
            if (locales.indexOf(code) !== -1) {
              locale = code;
              return false;
            }
          });

          var accept = $('#server').data('accept-language');
          if (accept) {
            accept = accept.toLowerCase();
            if (locales.indexOf(accept) !== -1) {
              locale = accept;
            }
          }
        }

        menu.find('.language.' + locale).click();
      });

      // Show only parts available for the selected project
      $('.part .selector').click(function () {
        var details = Pontoon.getProjectDetails(),
            menu = $(this).siblings('.menu').find('ul'),
            locale = $.trim($('.locale .selector .code').html().toLowerCase());

        if (details) {
          menu.find('li:not(".no-match")').remove();
          $(details[locale]).each(function() {
            var cls = '';

            if (this.name) {
              var title = this.name,
                  percent = '';

            } else {
              var title = this.resource__path,
                  share = 0;

              if (this.resource__entity_count > 0) {
                share = this.approved_count / this.resource__entity_count * 100;
              }

              percent = Math.floor(share) + '%';
            }

            if ($('#server').data('part') === title) {
              cls = ' class="current"';
            }

            menu.append('<li' + cls + '><span>' + title + '</span>' +
              '<span>' + percent + '</span></li>');
          });
        }

        $('.menu:visible input[type=search]').trigger("keyup");
      });

      // Parts menu handler
      $('.part .menu').on('click', 'li:not(".no-match")', function () {
        var title = $(this).find('span:first').html();
        $('.part .selector')
          .attr('title', title)
          .find('.title')
            .html(title.replace(/^.*[\\\/]/, ''));
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

      // Locale menu handler
      $('.locale .menu li:not(".no-match")').click(function () {
        var locale = $(this).find('.language').attr('class').split(' ')[1],
            // Escape special characters in CSS notation
            code = locale.replace( /(:|\.|\[|@|\])/g, "\\$1" ),
            language = $('.locale .menu .language.' + code).parent().html();

        // Request new locale
        if ($('.locale .menu .search-wrapper > a').is('.back:visible')) {
          var project = $('.project .title').data('slug');
          Pontoon.requestLocale(locale, project);

        // Select locale
        } else {
          $('.locale .selector').html(language);
        }

        var details = Pontoon.getProjectDetails(),
            locales = Object.keys(details),
            menu = $('.locale .menu'),
            locale = menu.siblings('.selector')
              .find('.code').html().toLowerCase();

        // Fallback if selected part not available for the selected project
        if (details[locale].length > 1) {
          var detail = details[locale][0],
              isPath = Object.keys(detail).indexOf("name") === -1,
              type = isPath ? 'resource__path' : 'name';
              part = $('.part .selector').attr('title');

          // Selected part available
          for (var d in details[locale]) {
            if (details[locale][d][type] === part) {
              $('header .part').removeClass("hidden");
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

      // Switch between available locales and locales to request
      $('.locale .menu .search-wrapper > a').click(function (e) {
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

      // Open selected project (part) and locale combination
      $('#go').click(function (e) {
        e.preventDefault();
        e.stopPropagation();

        var locale = $('.locale .selector .language').attr('class').split(' ')[1],
            project = $('.project .selector .title').data('slug'),
            part = $('.part .selector:visible').attr('title'),
            loc = '/' + locale + '/' + project;

        if (part) {
          loc += '/' + part;
        }
        window.location = loc;
      });

      // Profile menu
      // Register handlers to prep django-browserid before binding menu.
      django_browserid.registerWatchHandlers(function() {
        $('#profile .menu li').click(function (e) {
          e.preventDefault();

          if ($(this).is(".sign-out")) {
            window.location = '/signout/';

          } else if ($(this).is(".sign-in")) {
            self.startLoader();
            django_browserid.login().then(function(verifyResult) {
              var redirect = $('#server').data('redirect');
              if (redirect) {
                window.location = redirect;
              } else {
                window.location.reload();
              }
            }, function(jqXHR) {
              self.endLoader('Oops, something went wrong.', 'error');
            });

          } else if ($(this).data("url")) {
            window.location = $(this).data('url');

          } else if ($(this).is(".hotkeys")) {
            $('#hotkeys').show();
          }
        });
      });

      // Download menu
      $('#profile .menu .file-format').click(function (e) {
        e.preventDefault();

        if ($(this).is(".html")) {
          self.postMessage("HTML");
        } else {
          self.save($(this).attr('class').split(" ")[1]);
        }
      });

      // Close notification on click
      $('body > header').on('click', '.notification', function() {
        Pontoon.closeNotification();
      });

      function mouseMoveHandler(e) {
        var initial = e.data.initial,
            left = Math.min(Math.max(initial.leftWidth + e.pageX - initial.position, initial.leftMin),
                   initial.leftWidth + initial.rightWidth - initial.rightMin),
            right = Math.min(Math.max(initial.rightWidth - e.pageX + initial.position, initial.rightMin),
                    initial.leftWidth + initial.rightWidth - initial.leftMin);

        initial.left.width(left);
        initial.right.width(right).css('left', left);
      }

      function mouseUpHandler(e) {
        $(document)
          .unbind('mousemove', mouseMoveHandler)
          .unbind('mouseup', mouseUpHandler);
      }

      // Resize entity list and editor by dragging
      $('#drag-1').bind('mousedown', function (e) {
        e.preventDefault();

        var left = $('#entitylist'),
            right = $('#editor'),
            data = {
              left: left,
              right: right,
              leftWidth: left.outerWidth(),
              rightWidth: right.outerWidth(),
              leftMin: 250,
              rightMin: 350,
              position: e.pageX
            };

        left.css('transition-property', 'none');
        right.css('transition-property', 'none');

        $(document)
          .bind('mousemove', { initial: data }, mouseMoveHandler)
          .bind('mouseup', { initial: data }, mouseUpHandler);
      });

    },


    /*
     * Create user interface
     */
    createUI: function () {
      var self = this;

      // Show message if provided
      if ($('.notification li').length) {
        $('.notification').css('opacity', 100);
      }

      self.attachMainHandlers();
      self.renderEntityList();
      self.updateProgress();
      self.attachEditorHandlers();

      $("#project-load").hide();
      $("body > header > .container").show();

      // If 2-column layout opened by default, open first entity in the editor
      if (self.app.advanced) {
        $("#entitylist .entity:first").mouseover().click();
      }
    },


    /*
     * Resize iframe to fit space available
     */
    resizeIframe: function () {
      $('#source')
        .width($(window).width() - $('#sidebar:visible').width())
        .height($(window).height() - $('body > header').outerHeight());
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
          targetOrigin = targetOrigin || Pontoon.project.url,
          message = {
            type: messageType,
            value: messageValue
          };
      otherWindow.postMessage(JSON.stringify(message), targetOrigin);
    },


    /*
     * Handle messages from project code
     */
    receiveMessage: function (e) {
      var projectWindow = $('#source')[0].contentWindow;

      if (e.source === projectWindow) {
        var message = JSON.parse(e.data);

        switch (message.type) {

        case "READY":
          var advanced = false,
              websiteWidth = $('#server').data('width');

          $('body > header').show();
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
          Pontoon.paths = message.value;
          Pontoon.resizeIframe();
          Pontoon.initialize(advanced, projectWindow);
          break;

        case "DATA":
          // Deep copy: http://api.jquery.com/jQuery.extend
          Pontoon.entities = $.extend(
            true,
            Pontoon.entities,
            message.value.entities);
          break;

        case "RENDER":
          var value = message.value;
          Pontoon.project.url = value.url;
          Pontoon.project.title = value.title;
          Pontoon.createUI();
          Pontoon.syncLocalStorageOnServer();
          break;

        case "SWITCH":
          $("#switch").click();
          break;

        case "HOVER":
          Pontoon.entities[message.value].ui.addClass('hovered');
          break;

        case "UNHOVER":
          Pontoon.entities[message.value].ui.removeClass('hovered');
          break;

        case "ACTIVE":
          if ($('#switch').is('.opened')) {
            var entity = Pontoon.entities[message.value.id];
            Pontoon.openEditor(entity, message.value.inplace);
          }
          break;

        case "INACTIVE":
          if (!Pontoon.app.advanced && $("#editor").is('.opened')) {
            $('#cancel').trigger('click', [{inplace: true}]);
          }
          break;

        case "UPDATE":
          var entity = Pontoon.entities[message.value.id];
          Pontoon.updateOnServer(entity, message.value.content, true, true);
          break;

        case "DELETE":
          var entity = Pontoon.entities[message.value];
          Pontoon.updateEntityUI(entity);
          break;

        case "HTML":
          Pontoon.save("html", message.value);
          break;

        }
      }
    },

    /*
     * Make iFrame resizable
     */
    makeIframeResizable: function() {
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

      // Resize iframe with window
      $(window).resize(function () {
        Pontoon.resizeIframe();
        Pontoon.postMessage("RESIZE");
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
    },


    /*
     * Create Pontoon object data
     *
     * advanced Is advanced (2-column) mode on?
     * project Website window object
     */
    createObject: function (advanced, project) {
      var self = this;

      this.app = {
        win: window,
        advanced: advanced,
        path: $('#server').data('site-url') + '/' // pontoon.css injection
      };

      this.project = {
        win: project,
        url: "",
        title: "",
        pk: $('#server').data('id'),
        width: (
          $('#server').data('width') &&
          ($(window).width() - $('#server').data('width')) >= 700) ?
          $('#server').data('width') : false,
        links: $('#server').data('links')
      };

      this.locale = $('#server').data('locale');

      this.user = {
        email: $('#server').data('email') || '',
        name: $('#server').data('name') || '',
        localizer: $('#server').data('localizer'),
        manager: $('#server').data('manager')
      };
    },


    /*
     * Initialize Pontoon: load entities, store data, prepare UI
     */
    initialize: function(advanced, project) {
      var self = this;

      $.ajax({
        url: '/get-entities/',
        data: {
          project: $('#server').data('id'),
          locale: $('#server').data('locale').code,
          paths: JSON.stringify(/* Pontoon.paths || */[$('header .part .selector').attr('title')])
        },
        success: function(data) {
          if (data !== "error") {
            self.entities = data;

            // Projects with in place translation support
            if (project) {
              self.createObject(advanced, project);

              self.postMessage("INITIALIZE", {
                path: self.app.path,
                links: self.project.links,
                entities: self.entities,
                pk: self.project.pk,
                locale: self.locale,
                user: self.user
              }, null, $('#server').data('url'));

              self.makeIframeResizable();

            // Projects without in place translation support
            } else {
              $('body > header').show();
              $('#sidebar').addClass('advanced').css('width', '100%');
              $('#switch, #drag').remove();
              $('#editor').addClass('opened');

              self.createObject(true);

              $(self.entities).each(function (i) {
                this.id = i;
              });

              self.createUI();
              self.syncLocalStorageOnServer();
            }

          } else {
            $('#project-load')
              .find('.animation').hide().end()
              .find('.text')
                .html('Oops, something went wrong.')
                .animate({opacity: 1});
          }
        }
      });
    }

  });
}(Pontoon || {}));



/* Main code */
$(function() {

  // Start differently, depending on project URL
  var url = $('#server').data('url');

  if (url) {
    $('#source').attr('src', url);
    window.addEventListener("message", Pontoon.receiveMessage, false);

    var i = 0,
        interval = 0;

    // If no READY (Pontoon.paths) received for 10 seconds
    interval = setInterval(function() {
      i++;
      if (i > 100 && !Pontoon.paths) {
        clearInterval(interval);
        $('#source, #iframe-cover, #not-on-page, #profile .html').remove();
        window.removeEventListener("message", Pontoon.receiveMessage, false);
        return Pontoon.initialize();
      }
    }, 100);

  } else {
    Pontoon.initialize();
  }

  // Show potentially amusing message if loading takes more time
  setTimeout(function() {
    $('#project-load .text').animate({opacity: 1});
  }, 3000);

});
