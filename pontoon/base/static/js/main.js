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
        download(params);

      } else if (type === "transifex") {
        self.startLoader();

        params.strings = [];
        $("#entitylist .approved").each(function() {
          var entity = $(this)[0].entity;
          params.strings.push({
            original: entity.original,
            translation: entity.translation[0].string
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

      } else if (type === "repository-commit") {
        self.startLoader();

        if (value) {
          params.auth = {
            username: value[0].value,
            password: value[1].value,
            remember: value[2] ? 1 : 0
          };
        }

        $.ajax({
          url: 'commit-to-repository/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            data: JSON.stringify(params)
          },
          success: function(data) {
            if (data.type === "authenticate") {
              self.endLoader(data.message);
              $("#repository").show();

              // Move notification up
              var temp = $('.notification').css('top');
              $('.notification').css('top', '+=' + $('#repository').outerHeight());
              setTimeout(function() {
                $('.notification').css('top', temp);
              }, 2400); // Wait for close + fadeout

            } else if (data === "ok") {
              self.endLoader('Done!');
              $('#repository').hide();

            } else if (data.type === "error") {
              self.endLoader(self.doNotRender(data.message), 'error', true);
              $('#repository').hide();

            } else {
              self.endLoader('Oops, something went wrong.', 'error');
              $('#repository').hide();
            }
          },
          error: function() {
            self.endLoader('Oops, something went wrong.', 'error');
            $('#repository').hide();
          }
        });

      } else if (type === "repository-update") {
        self.startLoader();

        $.ajax({
          url: 'update-from-repository/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            data: JSON.stringify(params)
          },
          success: function(data) {
            if (data === "ok") {
              self.endLoader('Done!');
              // TODO: update entities with AJAX
              window.location.reload();

            } else if (data.type === "error") {
              self.endLoader(self.doNotRender(data.message), 'error', true);

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



    /*
     * Get translations to other locales of given entity
     *
     * entity Entity
     */
    getOtherLocales: function (entity) {
      var self = this,
          list = $('#other-locales ul').empty();

      if (self.XHRgetOtherLocales) {
        self.XHRgetOtherLocales.abort();
      }

      self.XHRgetOtherLocales = $.ajax({
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
     * target Target element jQuery selector
     */
    getMachinery: function (original, target) {
      var self = this,
          target = target || '#machinery'
          ul = $(target).find('ul').empty(),
          requests = 0;

      function complete(jqXHR, status) {
        if (status !== "abort") {
          requests--;
          if (requests === 0) {
            $('#helpers li a[href="#machinery"]').removeClass('loading');
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
            '<span class="stress">' + (data.quality || '') + '</span>' +
            '<a href="' + data.url + '" target="_blank"' +
              'title="' + data.title + '">' + data.source + '</a>' +
          '</header>' +
          '<p class="original">' + (data.original || '') + '</p>' +
          '<p class="translation">' + self.doNotRender(data.translation) +
          '</p>' +
        '</li>');
      }

      $('#helpers nav .active a').addClass('loading');

      // Translation memory
      requests++;

      if (self.XHRtranslationMemory) {
        self.XHRtranslationMemory.abort();
      }

      self.XHRtranslationMemory = $.ajax({
        url: 'translation-memory/',
        data: {
          text: original,
          locale: self.locale.code
        }

      }).success(function(data) {
        if (data.translations) {
          $.each(data.translations, function() {
            append({
              original: original,
              quality: '100%',
              url: self.app.path,
              title: 'Pontoon Homepage',
              source: 'Translation memory',
              translation: this
            });
          });
        }
      }).complete(complete);

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
        }).complete(complete);
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
        }).complete(complete);
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
      }).complete(complete);

      // Transvision
      requests++;

      if (self.XHRtransvision) {
        self.XHRtransvision.abort();
      }

      self.XHRtransvision = $.ajax({
        url: 'transvision/',
        data: {
          text: original,
          locale: self.locale.code
        }

      }).success(function(data) {
        if (data.translation) {
          append({
            original: original,
            quality: '100%',
            url: 'http://transvision.mozfr.org/',
            title: 'Visit Transvision',
            source: 'Mozilla',
            translation: data.translation
          });
        }
      }).complete(complete);
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
          list = $('#history ul').empty();

      if (self.XHRgetHistory) {
        self.XHRgetHistory.abort();
      }

      self.XHRgetHistory = $.ajax({
        url: 'get-history/',
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
                      ((self.user.email === this.user && !this.approved) ?
                        ' own' : '')) +
                    '">' +
                    '<div class="info">' +
                      this.user +
                      '<span class="stress">' + this.date + '</span>' +
                    '</div>' +
                    '<menu class="toolbar">' +
                      '<button class="approve fa" title="' +
                      (this.approved ? '' : 'Approve') +
                      '"></button>' +
                      '<button class="delete fa" title="Delete"></button>' +
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
      $("#editor")[0].entity = entity;

      // Metadata: comments, sources, keys
      $('#metadata').empty().hide();
      if (entity.comment) {
        $('#metadata').html('<span id="comment">' + entity.comment + '</span>').show();
      }
      if (entity.source) {
        $('#metadata').append('<a href="#" class="details">More details</a>').show();
        if (typeof(entity.source) === 'object') {
          $.each(entity.source, function() {
            $('#metadata').append('<span>#: ' + this.join(':') + '</span>');
          });
        } else {
          $('#metadata').append('<span>' + entity.source + '</span>');
        }
      }
      if (entity.key) {
        $('#metadata').append('<span>Key: ' + entity.key + '</span>');
      }

      // Original string and plurals
      $('#original').html(this.doNotRender(entity.original));
      $('#source-pane').removeClass('pluralized');
      $('#plural-tabs li').css('display', 'none');

      if (entity.original_plural) {
        $('#source-pane').addClass('pluralized');

        var nplurals = this.locale.nplurals;
        if (nplurals > 1) {

          // Get example number for each plural form based on locale plural rule
          if (!this.locale.examples) {
            var examples = this.locale.examples = {},
                rule = null,
                n = 0;

            if (nplurals === 2) {
              examples[0] = 1;
              examples[1] = 2;
            } else {
              while (Object.keys(examples).length < nplurals) {
                rule = eval(this.locale.plural_rule);
                if (!examples[rule]) {
                  examples[rule] = n;
                }
                n++;
              }
            }

            $('#plural-tabs li a span').each(function(i) {
              $(this).html(examples[i]);
              return i < nplurals-1;
            });
          }
          $('#plural-tabs li:lt(' + nplurals + ')').css('display', 'table-cell');
          $('#plural-tabs li:first a').click();
        }
      } else {
        $("#helpers nav .active a").click();
      }

      // Translation area
      $('#translation').val(entity.translation[0].string).focus();
      $('#warning:visible .cancel').click();

      // Length
      var original = entity['original' + this.isPluralized()].length,
          translation = entity.translation[0].string.length;

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
        if (entity.translation[i].pk) {
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
     * Switch to new entity in editor
     *
     * newEntity New entity we want to switch to
     */
    switchToEntity: function (newEntity) {
      var oldEntity = $('#editor')[0].entity;

      if (newEntity.body || (oldEntity && oldEntity.body)) {
        this.common.postMessage("NAVIGATE", newEntity.id);
      }
      if (!newEntity.body) {
        this.openEditor(newEntity);
      }
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
            .find('.string-wrapper' + ':not(":containsi("' + val + '")")')
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

        }

        searchEntities();
        $('#filter .title').html($(this).text());
        $('#filter .button').attr('class', 'button selector ' + type);
      });

      // Render
      $(self.project.entities).each(function () {
        var status = self.getEntityStatus(this),
            li = $('<li class="entity limited' +
          (status ? ' ' + status : '') +
          (!this.body ? ' uneditable' : '') + '">' +
          '<span class="status fa"></span>' +
          '<p class="string-wrapper">' +
            '<span class="source-string">' +
              self.doNotRender(this.original) +
            '</span><span class="translation-string">' +
              self.doNotRender(this.translation[0].string) +
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
        self.common.postMessage("HOVER", this.entity.id);
      }, function () {
        self.common.postMessage("UNHOVER", this.entity.id);
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
           pluralForm !== eval(plural_rule.replace("n", 1)))) {
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
          $('#cancel').click();
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
      $("#metadata a.details").live("click", function (e) {
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

      // Plurals navigation
      $("#plural-tabs a").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        $("#plural-tabs li").removeClass('active');
        $(this).parent().addClass('active');

        var i = $(this).parent().index(),
            editor = $('#editor')[0],
            entity = editor.entity,
            original = entity['original' + self.isPluralized()],
            title = !self.isPluralized() ? "Singular" : "Plural",
            source = entity.translation[i].string;

        $('#source-pane h2').html(title).show();
        $('#original').html(self.doNotRender(original));

        $('#translation').val(source).focus();
        $('#translation-length')
          .find('.original-length').html(original.length).end()
          .find('.current-length').html(source.length);

        $('#warning:visible .cancel').click();
        $("#helpers nav .active a").click();
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
          $('#save').click();
          return false;
        }

        // Esc: cancel translation and return to entity list
        if (key === 27) {
          if ($('#warning').is(':visible')) {
            $('#warning .cancel').click();
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

      // Update length (keydown is triggered too early)
      }).unbind("input propertychange").bind("input propertychange", function (e) {
        var length = $('#translation').val().length;
        $('#translation-length .current-length').html(length);

        $('#warning:visible .cancel').click();
      });

      // Close warning box
      $('#warning .cancel').click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        $('#warning')
          .find('ul').empty().end()
        .hide();
      });

      // Copy source to translation
      $("#copy").click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $('#editor')[0].entity,
            original = entity['original' + self.isPluralized()],
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
      $('#cancel').click(function (e, data) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $("#editor")[0].entity
            data = data || {};

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

        // Only if editable and not already handled inplace
        if (entity.body && !data.inplace) {
          self.common.postMessage("CANCEL");
          self.common.postMessage("UNHOVER", entity.id);
        }
      });

      // Save translation
      $('#save, #save-anyway').click(function (e) {
        e.stopPropagation();
        e.preventDefault();

        var entity = $('#editor')[0].entity,
            source = $('#translation').val();

        if (source === '' && self.project.format !== 'properties') {
          self.endLoader('Empty translations cannot be submitted.', 'error');
          return;
        }

        self.updateOnServer(entity, source);
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
          // Do not cache history to prevent outdate suggestions on return
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
      });

      // Custom search: trigger with Enter
      $('#custom-search input').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
        var value = $(this).val();
        if (e.which === 13 && value.length > 0) {
          self.getMachinery(value, "#custom-search");
          return false;
        }
      });

      // Copy helpers result to translation
      $("#helpers li:not('.disabled')").live("click", function (e) {
        e.stopPropagation();
        e.preventDefault();

        var translation = $(this).find('.translation').html(),
            source = self.doRender(translation);
        $('#translation').val(source).focus();
        $('#translation-length .current-length').html(source.length);

        $('#warning:visible .cancel').click();
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
          url: $(this).attr('class').split(' ')[0] + '-translation/',
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
                      translation = next.find('.translation').html();
                      entity.translation[pluralForm].string = translation;
                      entity.ui.find('.translation-string')
                        .html(self.doNotRender(translation));
                      entity.dirty = true;

                    // Last translation deleted, no alternative available
                    } else {
                      entity.dirty = false;
                      $('#translation').val('').focus();
                      if (entity.body && pluralForm === 0) {
                        self.common.postMessage("DELETE");
                      } else {
                        entity.translation[pluralForm].pk = null;
                        entity.translation[pluralForm].string = '';
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
          translated = $("#entitylist .entity.translated").length,
          approved = $("#entitylist .entity.approved").length,
          fuzzy = $("#entitylist .entity.fuzzy").length,
          percentTranslated = Math.round(translated * 100 / all),
          percentApproved = Math.round(approved * 100 / all),
          percentFuzzy = Math.round(fuzzy * 100 / all);

      $('#progress .translated').width(percentTranslated + '%');
      $('#progress .approved').width(percentApproved + '%');
      $('#progress .fuzzy').width(percentFuzzy + '%');
      $('#progress .number').html(approved + '|' + all);

      if (percentTranslated + percentApproved + percentFuzzy> 50) {
        $('#progress .number').addClass('left');
      } else {
        $('#progress .number').removeClass('left');
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
        .html(this.doNotRender(translation));

      this.updateProgress();
    },



    /*
     * Update entity translation on server
     * 
     * entity Entity
     * translation Translation
     * inplace Was translation submitted in-place?
     */
    updateOnServer: function (entity, translation, inplace) {
      var self = this,
          pluralForm = self.getPluralForm();

      self.startLoader();

      function gotoEntityListOrNextEntity() {
        // Go to entity list
        if (!self.app.advanced && $("#editor").is('.opened')) {
          $('#cancel').click();

        // Go to next entity
        } else {
          $('#next').click();
        }
      }

      $.ajax({
        url: 'update/',
        type: 'POST',
        data: {
          csrfmiddlewaretoken: $('#server').data('csrf'),
          locale: self.locale.code,
          entity: entity.pk,
          translation: translation,
          plural_form: pluralForm,
          original: entity['original' + self.isPluralized()],
          ignore_check: inplace || $('#warning').is(':visible')
        },
        success: function(data) {
          if (data.type) {
            self.endLoader('Translation ' + data.type);

            var pf = self.getPluralForm(true);
            entity.translation[pf] = data.translation;
            self.updateEntityUI(entity);

            // Update translation, including in-place if possible
            if (!inplace && entity.body && (self.user.localizer ||
                !entity.translation[pf].approved)) {
              self.common.postMessage("SAVE", translation);
            }

            // Quit
            if (!$("#editor").is('.opened')) {
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
            $('#warning ul').empty();
            $(data.warnings).each(function() {
              $('#warning ul').append('<li>' + this + '</li>');
            });
            $('#warning').show();

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
      $('.notification').fadeOut();
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
          .html(text)
          .removeClass().addClass('notification ' + type)
          .show()
          .click(function() {
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
      $('#profile .menu li').click(function (e) {
        e.preventDefault();
        if ($(this).is(".sign-out")) {
          window.location = 'signout/';
        } else if ($(this).is(".admin") || $(this).is(".project-admin")) {
          window.location = $(this).data('url');
        } else if ($(this).is(".html")) {
          self.common.postMessage("HTML");
        } else {
          self.save($(this).attr('class').split(" ")[0]);
        }
      });

      // Transifex and repository authentication
      $('.popup').find('.cancel').click(function (e) {
        e.preventDefault();
        $('.popup').hide();
      }).end().find('.button').click(function (e) {
        e.preventDefault();
        var type = $(this).parents('.popup').attr('id');
        self.save(type, $('#' + type + ' form').serializeArray());
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

      self.attachMainHandlers();
      self.renderEntityList();
      self.updateProgress();
      self.attachEditorHandlers();

      $("#spinner").fadeOut(function() {
        $("#pontoon > header > .container").fadeIn();
      });

      // If 2-column layout opened by default, open first entity in the editor
      if (self.app.advanced) {
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
          if (!Pontoon.app.advanced && $("#editor").is('.opened')) {
            $('#cancel').trigger('click', [{inplace: true}]);
          }
          break;

        case "UPDATE":
          var entity = Pontoon.project.entities[message.value.id];
          Pontoon.updateOnServer(entity, message.value.content, true);
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
     * advanced Is advanced (2-column) mode on?
     * project Website window object
     */
    init: function (app, advanced, project) {
      var self = this;

      // Build Pontoon object
      this.app = {
        win: app,
        advanced: advanced,
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
        }, null, $('#server').data('url'));

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
     * Common functions used in both, client specific code and Pontoon library
     */
    common: (function () {
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
          $('body:not(".admin-project") .search:visible').focus();
        }
      });

      // Hide menus on click outside
      $('body:not(".admin-project")').click(function () {
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
            project = $('.project .selector .title').data('slug'),
            page = $('.page .selector .title:visible').html(),
            loc = locale + '/' + project;

        // On homepage, show error if no project selected
        if (!locale) {
          Pontoon.common.showError("Oops, no project selected.");
          return;
        }

        if (page) {
          loc += '/' + page;
        }
        window.location = loc;
      });

      // Project menu handler
      $('.project .menu li:not(".no-match")').bind('click.main', function () {
        var name = $(this).find('.project-name').html(),
            slug = $(this).find('.project-name').data('slug');

        $('.project .selector .title')
          .html(name)
          .data('slug', slug);

        if ($('body').is('.admin')) {
          return false;
        }

        // Fallback if selected page not available for the selected project
        var defaultPage = Pontoon.common.getProjectResources('pages')[0];
        if (defaultPage) {
          $('.page .selector .title').html(defaultPage);
          $('header .page').removeClass("hidden")
            .find('.selector .title').html(defaultPage);
        } else {
          $('header .page').addClass("hidden");
        }

        // Fallback if selected locale not available for the selected project
        var locales = Pontoon.common.getProjectResources('locales'),
            menu = $('.locale .menu'),
            selector = menu.siblings('.selector'),
            selected = selector.find('.code').html(),
            accept = $('#server').data('accept-language').toLowerCase();

        if (locales.indexOf(selected) === -1) {
          var code = (locales.indexOf(accept) !== -1) ? accept : locales[0];
          var defaultLocale =
            menu.find('.language.' + code)[0].outerHTML;
          selector.html(defaultLocale);
        }
      });

      // Page menu handler
      $('.page .menu li:not(".no-match")').live("click.pontoon", function () {
        var title = $(this).html();
        $('.page .selector .title').html(title);
      });

      // Locale menu handler
      $('body:not(".admin-project") .locale .menu li:not(".no-match")').click(function () {
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

      // General keyboard shortcuts
      $('html').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        var key = e.which;

        if ($('.menu').is(':visible')) {
          var menu = $('.menu:visible'),
              hovered = menu.find('li.hover');

          // Up arrow: move up
          if (key === 38) {
            if (hovered.length === 0 ||
                menu.find('li:visible:first').is('.hover')) {
              menu.find('li.hover').removeClass('hover');
              menu.find('li:visible:last').addClass('hover');
            } else {
              menu.find('li.hover').removeClass('hover')
                .prevAll(':visible:not(".horizontal-separator"):first')
                  .addClass('hover');
            }
            if (menu.parent().is('.locale')) {
              Pontoon.updateScroll(menu.find('ul'));
            }
            if (menu.parent().is('.project')) {
              var type = (!$('body').is('.admin')) ?
                '.project-url' : '.project-name';
              $('.url').val($('.project .menu li.hover').find(type).html());
            }
            return false;
          }

          // Down arrow: move down
          if (key === 40) {
            if (hovered.length === 0 ||
                menu.find('li:visible:last').is('.hover')) {
              menu.find('li.hover').removeClass('hover');
              menu.find('li:visible:first').addClass('hover');
            } else {
              menu.find('li.hover').removeClass('hover')
                .nextAll(':visible:not(".horizontal-separator"):first')
                  .addClass('hover');
            }
            if (menu.parent().is('.locale')) {
              Pontoon.updateScroll(menu.find('ul'));
            }
            if (menu.parent().is('.project')) {
              var type = (!$('body').is('.admin')) ?
                '.project-url' : '.project-name';
              $('.url').val($('.project .menu li.hover').find(type).html());
            }
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
          if (Pontoon.app.advanced || $("#editor").is('.opened')) {
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
              targetOrigin = targetOrigin || Pontoon.project.url,
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
