/* Extend public object */
var Pontoon = (function (my) {

  return $.extend(true, my, {
    /*
     * UI helper methods
     *
     * type - if specified, function returns value for this filter type otherwise for all types
     */
    getFilter: function(type) {
      return type ? $('#filter').data('current-filter')[type] : $('#filter').data('current-filter');
    },


    getSearch: function() {
      return $('#search').val();
    },


    setSearch: function(value) {
      $('#search').val(value);
    },


    renderEntity: function (index, entity) {
      var self = this,
          status = self.getEntityStatus(entity),
          openSans = (['Latin', 'Greek', 'Cyrillic', 'Vietnamese'].indexOf(self.locale.script) > -1) ? ' open-sans' : '',
          sourceString = (entity.original_plural && self.locale.nplurals < 2) ? entity.marked_plural : entity.marked,
          translation = entity.translation[0],
          translationString = translation.string || '';

      sourceString = self.fluent.getSimplePreview(entity, sourceString, entity);
      translationString = self.fluent.getSimplePreview(translation, translationString, entity);

      var li = $('<li class="entity' +
        (' ' + status) +
        (!entity.body ? ' uneditable' : '') +
        (this.allEntitiesSelected ? ' selected' : '') +
        (entity.visible ? ' visible': '') +
        '" data-entry-pk="' + entity.pk + '">' +
        '<span class="status fa' + (self.user.canTranslate() ? '' : ' unselectable') + '"></span>' +
        '<p class="string-wrapper">' +
          '<span class="source-string">' + sourceString + '</span>' +
          '<span class="translation-string' + openSans + '" dir="' + self.locale.direction + '" lang="' + self.locale.code + '" data-script="' + self.locale.script + '">' +
            self.markPlaceables(translationString) +
          '</span>' +
        '</p>' +
        '<span class="arrow fa fa-chevron-right fa-lg"></span>' +
        '</li>', self.app.win);
      li[0].entity = entity;
      entity.ui = li; /* HTML Element representing string in the main UI */
      self.highlightQuery(li);

      // Hover editable entities on the page
      if (entity.body) {
        li.hover(function () {
          self.postMessage("HOVER", entity.id);
        }, function () {
          self.postMessage("UNHOVER", entity.id);
        });
      }

      // Open entity editor on click
      li.click(function (e) {
        // Status icons are used to select entities for batch operations
        if ($(e.target).is('.status:not(".unselectable")')) {
          return;
        }

        self.switchToEntity(this.entity);
      });
      return entity;
    },


    /*
     * Append entity to the appropriate section of the entity list
     */
    appendEntity: function (entity) {
      var section = entity.body ? '.editables' : '.uneditables';
      $('#entitylist .wrapper').find(section).append(entity.ui);
    },


    /*
     * Display entity in the entity list
     *
     * Used only with in-place editor, which allows any entity to be selected
     * and thus requires them to be available in the sidebar all the time
     */
    showEntity: function (entity) {
      $('#entitylist .entity[data-entry-pk=' + entity.pk + ']').show();
    },


    /*
     * Hides all previously loaded entities
     */
    hideEntities: function() {
      $('#entitylist .entity').hide();
      this.setNotOnPage();
    },


    /*
     * Show/hide Not on current page heading when needed
     */
    setNotOnPage: function () {
      var uneditablesVisible = $('.uneditables .entity:visible').length > 0;
      $('#not-on-page:not(".hidden")').toggle(uneditablesVisible);
    },


    /*
     * Get suggestions from other locales
     */
    getOtherLocales: function (entity) {
      var self = this,
          list = $('#helpers .other-locales ul').empty(),
          tab = $('#helpers a[href="#other-locales"]'),
          count = '',
          preferred = 0,
          remaining = 0,
          localesOrder = self.user.localesOrder;

      self.NProgressUnbind();

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
          if (data.length) {
            $.each(data, function() {
              var translationString = self.fluent.getSimplePreview(this, this.string, entity),
              link = self.getResourceLink(
                    this.locale__code,
                    self.project.slug,
                    self.part,
                    entity.pk
                  );

              list.append('<li class="suggestion" title="Copy Into Translation (Tab)">' +
                '<header>' +
                  '<a href="' + link + '" title="" target="_blank">' + this.locale__name + '<span class="stress">' + this.locale__code + '</span></a>' +
                '</header>' +
                '<p class="translation" dir="' + this.locale__direction + '" lang="' + this.locale__code + '" data-script="' + this.locale__script + '">' +
                  self.markPlaceables(translationString) +
                '</p>' +
                '<p class="translation-clipboard">' +
                  self.doNotRender(this.string) +
                '</p>' +
              '</li>');

              if (!$.isEmptyObject(localesOrder) && localesOrder.indexOf(this.locale__code) > -1) {
                preferred += 1;
              }
            });

            count = data.length;
            remaining = count - preferred;

            if (!$.isEmptyObject(localesOrder)) {
              var sortedItems = list.find('li').sort(function(a, b) {
                 var localeA = $(a).find('p').prop('lang'),
                     localeB = $(b).find('p').prop('lang');

                 var valA = localesOrder.indexOf(localeA),
                     valB = localesOrder.indexOf(localeB);

                 return (valA === -1 && valB === -1 ) ? localeA > localeB : (valA < valB) ? 1 : (valA > valB) ? -1 : 0;
              });

              list.children('li').remove();

              sortedItems.each(function() {
                list.append(this);
              });

              if (preferred > 0 && remaining > 0) {
                list.find('li:eq(' + (preferred-1) + ')').addClass('preferred');
              }
            }

          } else {
            list.append('<li class="disabled"><p>No translations available.</p></li>');
          }
        },
        error: function(error) {
          if (error.status === 0 && error.statusText !== "abort") {
            // Allows requesting locales again
            editor.otherLocales = null;
            self.noConnectionError(list);
          } else {
            list.append('<li class="disabled"><p>No translations available.</p></li>');
          }
        },
        complete: function() {
          tab
            .find('.count')
              .find('.preferred').html(preferred).toggle(preferred > 0).end()
              .find('.plus').html('+').toggle(preferred > 0 && remaining > 0).end()
              .find('.remaining').html(remaining).toggle(remaining > 0).end()
              .toggle(count !== '');
        }
      });

      self.NProgressBind();
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


    getApproveButtonTitle: function(translation) {
      if (translation.approved && translation.approved_user) {
        return 'Approved by ' + translation.approved_user;
      } else {
        if (translation.unapproved_user) {
          return 'Unapproved by ' + translation.unapproved_user;
        } else {
          return 'Not reviewed yet';
        }
      }

    },


    /*
     * Get history of translations of given entity
     *
     * entity Entity
     */
    getHistory: function (entity) {
      var self = this,
          list = $('#helpers .history ul').empty(),
          tab = $('#helpers a[href="#history"]'),
          count = '';

      self.NProgressUnbind();

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
          if (data.length) {
            $.each(data, function(i) {
              var baseString = self.fluent.getSimplePreview(data[0], data[0].string, entity),
                  translationString = self.fluent.getSimplePreview(this, this.string, entity);

              list.append(
                '<li data-id="' + this.pk + '" class="suggestion ' +
                (this.approved ? 'translated' : this.rejected ? 'rejected' : this.fuzzy ? 'fuzzy' : 'suggested') +
                '" title="Copy Into Translation (Tab)">' +
                  '<header class="clearfix' +
                    ((self.user.canTranslate()) ? ' translator' :
                      ((self.user.id === this.uid && !this.approved) ?
                        ' own' : '')) +
                    '">' +
                    '<div class="info">' +
                      ((!this.uid) ? '<span>' + this.user + '</span>' :
                        '<a href="/contributors/' + this.username + '" title="' + self.getApproveButtonTitle(this) + '">' + this.user + '</a>') +
                      '<time dir="ltr" class="stress" datetime="' + this.date_iso + '">' + this.date + ' UTC</time>' +
                    '</div>' +
                    '<menu class="toolbar">' +
                      ((i > 0) ? '<a href="#" class="toggle-diff" data-alternative-text="Hide diff" title="Show diff against the currently active translation">Show diff</a>' : '') +
                      '<button class="' + (this.approved ? 'unapprove' : 'approve') + ' fa" title="' +
                       (this.approved ? 'Unapprove' : 'Approve')  + '"></button>' +
                      ((self.user.id && (self.user.id === this.uid) || self.user.canTranslate()) ? '<button class="' +
                       (this.rejected ? 'unreject' : 'reject') + ' fa" title="' +
                       (this.rejected ? 'Unreject' : 'Reject') + '"></button>' : '') +
                    '</menu>' +
                  '</header>' +
                  '<p class="translation" dir="' + self.locale.direction + '" lang="' + self.locale.code + '" data-script="' + self.locale.script + '">' +
                    self.markPlaceables(translationString) +
                  '</p>' +
                  '<p class="translation-diff" dir="' + self.locale.direction + '" lang="' + self.locale.code + '" data-script="' + self.locale.script + '">' +
                    ((i > 0) ? self.diff(baseString, translationString) : self.markPlaceables(translationString)) +
                  '</p>' +
                  '<p class="translation-clipboard">' +
                    self.doNotRender(this.string) +
                  '</p>' +
                '</li>');
            });

            $("#helpers .history time").timeago();
            count = data.length;

          } else {
            list.append('<li class="disabled"><p>No translations available.</p></li>');
          }
        },
        error: function(error) {
          if (error.status === 0 && error.statusText !== "abort") {
            self.noConnectionError(list);
          }
        },
        complete: function() {
          tab.find('.count').html(count).toggle(count !== '');
        }
      });

      self.NProgressBind();
    },


    /*
     * Get suggestions for currently translated entity from all helpers
     */
    updateHelpers: function () {
      var entity = this.getEditorEntity(),
          source = this.fluent.getSimplePreview(entity, entity['original' + this.isPluralized()], entity);

      this.getHistory(entity);

      // Hard to match plural forms with other locales; using singular
      this.getOtherLocales(entity);

      if (this.machinerySource !== source) {
        this.getMachinery(source);
        this.machinerySource = source;
      }

      var tab = $("#helpers nav .active a"),
          section = tab.attr('href').substr(1);

      $('#helpers section.' + section + ':hidden').show();
    },


    /*
     * Append source string metadata
     *
     * title Metadata title
     * text Metadata text
     * link Metadata link (optional)
     */
    appendMetaData: function (title, text, link, linkClass) {
      if (link) {
        text = '<a href="' + link + '" class="' + linkClass + '">' + this.doNotRender(text) + '</a>';
      }

      $('#metadata').append('<p><span class="title">' + title + '</span> <span class="content">' + text + '</span></p>');
    },


    /**
     * Jump to a part without reloading the whole UI
     */
    jumpToPart: function(part) {
      var self = this;

      self.checkUnsavedChanges(function() {
        $('.part .selector').attr('title', part);
        self.updateCurrentPart(part);

        // Reset optional state parameters and update state
        self.setSearch('');
        self.updateFilterUI(self.getEmptyFilterObject());

        var state = self.getState('selected');
        state.entity = null;
        self.pushState(state);

        self.initializePart(true);
      });
    },


    /*
     * Return a link to resource from a set of given parameters.
     */
    getResourceLink: function(localeCode, projectSlug, resourcePath, entityId) {
      var link = '/' + localeCode + '/' +  projectSlug + '/' + resourcePath + '/';

      if (entityId) {
        link += '?string=' + entityId;
      }

      return link;
    },


    /*
     * Move cursor to the beginning of translation textarea
     */
    moveCursorToBeginning: function () {
      var element = $('#editor textarea:visible:first');
      if (element.length) {
        element[0].setSelectionRange(0, 0);
      }
    },


    /*
     * Update current translation length
     */
    updateCurrentTranslationLength: function () {
      var limit = this.translationLengthLimit,
          translation = $('#editor textarea:visible:first').val() || '';

      if (limit) {
        var length = this.stripHTML(translation).length,
            charactersLeft = limit - length;

        $('#translation-length .characters-left')
          .toggleClass('overflow', charactersLeft < 0)
          .html(charactersLeft);

      } else {
        $('#translation-length .current-length')
          .html(translation.length);
      }
    },


    /*
     * Update cached translation, needed for unsaved changes check
     */
    updateCachedTranslation: function () {
      this.cachedTranslation = this.fluent.getTranslationSource();
    },


    /*
     * Update the standard translation editor and focus it
     */
    updateAndFocusTranslationEditor: function (translation) {
      $('#editor textarea:visible:first').val(translation).focus();
    },


    /*
     * Open batch editor
     */
    openBatchEditor: function (loading) {
      var self = this;

      self.checkUnsavedChanges(function() {
        $('#sidebar').addClass('batch');

        loading = loading || false;
        $('#sidebar .batch-bar').toggleClass('selecting-all-entities', loading)
          .find('.variant').toggleClass('plural', self.selectedEntities.length > 1).end()
          .find('.selected-count').html(self.selectedEntities.length);

        $('#batch')
          .find('button').removeClass('loading confirmed show-message')
            .find('.message').html('');
      });
    },


    /*
     * Get example number for each plural form based on locale plural rule
     */
    generateLocalePluralExamples: function () {
      var self = this;
      var nplurals = self.locale.nplurals;
      var cldr_plurals = self.locale.cldr_plurals;

      if (nplurals === 2) {
        self.locale.plural_examples = {};
        self.locale.plural_examples[cldr_plurals[0]] = 1;
        self.locale.plural_examples[cldr_plurals[1]] = 2;

      } else {
        var examples = self.locale.plural_examples = {};

        // Example candidate: n is a variable used in the eval()
        var n = 0;

        while (Object.keys(examples).length < nplurals) {
          var rule = eval(self.locale.plural_rule);
          if (!examples[cldr_plurals[rule]]) {
            examples[cldr_plurals[rule]] = n;
          }
          n++;
        }
      }

      // Update plural tabs
      $.each(cldr_plurals, function(i) {
        $('#plural-tabs li:eq(' + i + ') a')
          .find('span').html(this).end()
          .find('sup').html(self.locale.plural_examples[this]);
      });
    },


    /*
     * Open translation editor in the main UI
     *
     * entity Entity
     */
    openEditor: function (entity) {
      var self = this;
      self.translationLengthLimit = null;

      $('#editor')[0].entity = entity;

      // Metadata: comment
      $('#metadata').empty();
      $('#source-pane').removeClass().find('#screenshots').empty();

      if (entity.comment) {
        // Translation length limit
        var split = entity.comment.split('\n'),
            splitComment = entity.comment;
        if (split[0].startsWith('MAX_LENGTH')) {
          try {
            self.translationLengthLimit = parseInt(split[0].split('MAX_LENGTH: ')[1].split(' ')[0], 10);
            splitComment = split.length > 1 ? entity.comment.substring(entity.comment.indexOf('\n') + 1) : '';
          } catch (e) {
            // Catch unexpected comment structure
          }
        }

        var comment = this.linkify(splitComment);
        if (comment === splitComment) {
          comment = this.doNotRender(splitComment);
        }
        self.appendMetaData('Comment', comment);

        // Screenshot
        $('#metadata').find('a').each(function() {
          var url = $(this).html();
          if (/(https?:\/\/.*\.(?:png|jpg))/im.test(url)) {
            var localURL = url.replace(/en-US\//gi, self.locale.code + '/');
            $('#screenshots').append('<img src="'+ localURL +'" alt="Screenshot">');
            $('#source-pane').addClass('screenshots');
          }
        });
      }

      // Metadata: key
      if (entity.key) {
        self.appendMetaData('Context', entity.key);
      }

      // Metadata: source
      if (entity.source) {
        if (typeof(entity.source) === 'object') {
          $.each(entity.source, function() {
            self.appendMetaData('#:', this.join(':'));
          });
        } else {
          self.appendMetaData('Source', entity.source);
        }
      }

      // Metadata: path
      if (entity.path) {
        var link = null,
            linkClass = null;

        // Resources can be mapped into multiple subpages.
        if (!entity.project.url) {
          link = self.getResourceLink(
            self.locale.code,
            entity.project.slug,
            entity.path
          );

          if (self.project.slug !== 'all-projects') {
            linkClass = 'resource-path';
          }
        }

        self.appendMetaData('Resource', entity.path, link, linkClass);
      }

      // Metadata: project
      var projectLink = '/' + self.locale.code + '/' +  entity.project.slug + '/';
      self.appendMetaData('Project', entity.project.name, projectLink);

      // Original string and plurals
      $('#original').html(entity.marked);
      $('#source-pane').removeClass('pluralized');
      $('#plural-tabs li').css('display', 'none');

      if (entity.original_plural) {
        $('#source-pane').addClass('pluralized');

        var nplurals = this.locale.nplurals;
        if (nplurals > 1) {
          $('#plural-tabs li:lt(' + nplurals + ')').css('display', 'table-cell');
          $('#plural-tabs li:first a').click();

        // Show plural string to locales with a single plural form (includes variable identifier)
        } else {
          $('#source-pane h2').html('Plural').show();
          $('#original').html(entity.marked_plural);
        }
      }

      // Translation area (must be set before unsaved changes check)
      var translation = entity.translation[0];
      $('#translation').val(translation.string);
      $('.warning-overlay:visible .cancel').click();

      // Length
      var original = entity['original' + this.isPluralized()];

      // Toggle translation length display
      $('#translation-length')
        .find('.current-vs-original').toggle(!self.translationLengthLimit).end()
        .find('.countdown').toggle(!!self.translationLengthLimit);

      // Need to show if sidebar opened by default
      $('#translation-length').show().find('.original-length').html(original.length);
      self.moveCursorToBeginning();
      self.updateCurrentTranslationLength();

      // Update entity list
      $("#entitylist .hovered").removeClass('hovered');
      entity.ui.addClass('hovered');
      this.updateScroll($('#entitylist .wrapper'));

      // Switch editor and entitylist in 1-column layout
      if (!this.app.advanced) {
        $("#entitylist").css('left', -$('#sidebar').width());
        $("#editor").addClass('opened').css('left', 0);
      }

      // FTL: Complex original string and translation
      self.fluent.toggleOriginal();
      self.fluent.toggleEditor();

      if (self.fluent.isFTLEditorEnabled()) {
        self.fluent.renderEditor();
      }

      self.fluent.toggleButton();

      self.updateCachedTranslation();
      self.updateHelpers();
      self.pushState();
    },


    /*
     * Get entity status: 'translated', 'fuzzy', 'suggested', 'partial', 'missing'
     *
     * entity Entity
     */
    getEntityStatus: function (entity) {
      var translation = entity.translation,
          translated = 0,
          fuzzy = 0,
          suggested = 0;

      for (var i=0; i<translation.length; i++) {
        if (entity.translation[i].approved) {
          translated++;
        }
        if (entity.translation[i].fuzzy) {
          fuzzy++;
        }
        // Include empty and anonymous translations
        if (entity.translation[i].pk || entity.translation[i].string) {
          suggested++;
        }
      }

      if (i === translated) {
        return 'translated';
      } else if (i === fuzzy) {
        return 'fuzzy';
      } else if (i === suggested) {
        return 'suggested';
      } else if (translated > 0 || fuzzy > 0 || suggested > 0) {
        return 'partial';
      }
      return 'missing';
    },


    /*
     * Check unsaved changes in editor
     *
     * callback Callback function
     */
    checkUnsavedChanges: function (callback) {
      var entity = this.getEditorEntity();

      if (!entity) {
        this.restoreInPlaceTranslation();
        return callback();
      }

      var before = this.cachedTranslation,
          after = this.fluent.getTranslationSource();

      if ((before !== null) && (before !== after)) {
        $('#unsaved').show();
        $('#editor textarea:visible:first').focus();
        this.checkUnsavedChangesCallback = callback;

      } else {
        this.restoreInPlaceTranslation();
        return callback();
      }
    },


    /*
     * Do not change anything in place and hide editor
     */
    stopInPlaceEditing: function () {
      var entity = this.getEditorEntity();

      if (entity.body) {
        this.postMessage("CANCEL");
        this.postMessage("UNHOVER", entity.id);
      }
    },


    /*
     * Close editor and return to entity list
     */
    goBackToEntityList: function () {
      $("#entitylist")
        .css('left', 0)
        .find('.hovered').removeClass('hovered');

      $("#editor")
        .removeClass('opened')
        .css('left', $('#sidebar').width());
      this.pushState();
    },


    /*
     * Navigate to next/previous entity in editor
     */
    navigateToEntity: function (type) {
      var entitySelector = '#entitylist .entity:visible',
          index = this.getEditorEntity().ui.index(entitySelector),
          step = type === 'next' ? 1 : -1,
          fallback = type === 'next' ? ':first' : ':last',
          newEntity = $(entitySelector).eq(index + step);

      if (newEntity.length === 0) {
        newEntity = $(entitySelector + fallback);
      }

      this.switchToEntity(newEntity[0].entity);
    },


    /*
     * Switch to new entity in editor
     *
     * newEntity New entity we want to switch to
     */
    switchToEntity: function (newEntity) {
      var self = this;

      self.checkUnsavedChanges(function() {
        // We must hide batch editor first in order to display FTL editor properly
        self.clearSelection();

        var oldEntity = self.getEditorEntity();

        if (newEntity.body || (oldEntity && oldEntity.body)) {
          self.postMessage("NAVIGATE", newEntity.id);
        }
        if (!newEntity.body) {
          self.openEditor(newEntity);
        }
      });
    },


    /*
     * Clear selected entities
     */
    clearSelection: function () {
      $('#sidebar').removeClass('batch');
      $('#entitylist .entity.selected').removeClass('selected');
      this.allEntitiesSelected = false;
    },


    /*
     * Search list of entities using the search field value
     */
    searchEntities: function () {
      this.hasNext = true;
      if (this.requiresInplaceEditor()) {
        this.hideEntities();
      } else {
        this.cleanupEntities();
      }
      this.loadNextEntities();
    },

    /*
     * Render list of entities to translate
     */
    renderEntityList: function () {
      var self = this;

      $($(self.entities).map($.proxy(self.renderEntity, self))).each(function (idx, entity) {
        self.appendEntity(entity);
      });

      self.setNotOnPage();
    },


    /*
     * Select entities for batch editing panel
     */
    selectEntity: function (entity, event) {
      var self = this;

      // Select single entity
      entity.toggleClass('selected');

      // Select multiple entities if holding Shift
      if (event.shiftKey && self.lastSelectedEntity) {
        var entities = $('#entitylist .entity'),
            start = entities.index(entity),
            end = entities.index(self.lastSelectedEntity);

        entities
          .slice(Math.min(start, end), Math.max(start, end) + 1)
            .toggleClass('selected', entity.is('.selected'));
      }

      $('#entitylist .hovered').removeClass('hovered');

      // Update selected entities
      if (self.allEntitiesSelected) {
        $('#entitylist .entity:not(".selected")').each(function() {
          var index = self.selectedEntities.indexOf(this.entity.pk);
          if (index !== -1) {
            self.selectedEntities.splice(index, 1);
          }
        });
        $('#entitylist .entity.selected').each(function() {
          var pk = this.entity.pk,
              index = self.selectedEntities.indexOf(pk);
          if (index === -1) {
            self.selectedEntities.push(pk);
          }
        });

      } else {
        self.selectedEntities = self.getEntitiesIds('#entitylist .entity.selected');
      }

      // If at least one entity selected, open batch editor
      if (self.selectedEntities.length > 0) {
        self.openBatchEditor();

      // If not, open regular editor
      } else {
        if (self.app.advanced) {
          entity.addClass('hovered');
          self.switchToEntity(entity[0].entity);
        }

        self.clearSelection();
      }

      self.lastSelectedEntity = entity;
    },


    /*
     * Start/Stop costumizing time range
     */
    toggleRangeEditing: function() {
      var editing = $('.for-time-range .edit').is('.editing');
      $('#range-picker').toggle(!editing);

      $('#filter .time-range')
        .toggleClass('editing', !editing)
        .find('input').each(function() {
          $(this).prop('disabled', editing);
        });

      var $toggle = $('#filter .horizontal-separator .edit'),
          newTitle = $toggle.data('alternative'),
          oldTitle = $toggle.html();

      $toggle
        .html(newTitle)
        .data('alternative', oldTitle)
        .toggleClass('editing');

      this.positionFilterToolbar();
    },


    /*
     * Reverse day and month order
     */
    reverseDayMonth: function(date) {
      var split = date.split('/');
      return split[1] + '/' + split[0] + '/' + split[2];
    },


    /*
     * Convert server time to local format
     */
    server2local: function(d) {
      return ('0' + d.getDate()).slice(-2) + '/' +
      ('0' + (d.getMonth() + 1)).slice(-2) + '/' +
      d.getFullYear() + " " +
      ('0' + d.getHours()).slice(-2) + ":" +
      ('0' + d.getMinutes()).slice(-2);
    },


    /*
     * Convert local time to to server format and time zone (UTC)
     */
    local2server: function(local) {
      var reverse = this.reverseDayMonth(local);

      try {
        var utc = new Date(reverse).toISOString();
        return utc.replace(/-/gi, '').replace(/T/gi, '').replace(/:/gi, '').substring(0, 12);
      } catch (e) {
        // fail silently ?
      }
    },


    /*
     * Convert local time to chart format (Epoch) and time zone (UTC)
     */
    local2chart: function(local) {
      var reverse = this.reverseDayMonth(local);
      return new Date(reverse).getTime();
    },


    /*
     * Initialize Time Range selector chart
     */
    updateRangePicker: function(counts) {
      $('#filter').find('.time-range, .for-time-range').toggle(counts.length > 0);

      if (counts.length === 0) {
        return;
      }

      // Set default input values and limits if values not set

      if (!$('#from').val() || !$('#to').val()) {
        var from = counts[0][0],
            to = counts[counts.length - 1][0];

        $('#from').val(Highcharts.dateFormat('%d/%m/%Y %H:%M', from));
        $('#to').val(Highcharts.dateFormat('%d/%m/%Y %H:%M', to));
      }

      // Render range selector
      Highcharts.setOptions({
        global: {
            useUTC: false
        },
        lang:{
          rangeSelectorZoom: ''
        }
      });

      $('#range-picker').highcharts('StockChart', {
        credits: {
          enabled: false
        },

        title: {
          enabled: false
        },

        scrollbar : {
          enabled : false
        },

        tooltip: {
          enabled: false
        },

        chart: {
          backgroundColor: 'transparent',
          marginLeft: 5,
          marginRight: 4,
          spacingBottom: 30,
          spacingTop: 0,
          style: {
            fontFamily: 'inherit'
          }
        },

        xAxis: {
          lineWidth: 0,
          tickLength : 0,
          labels: {
            enabled: false
          },
          events: {
            setExtremes: function (e) {
              $('#from').val(Highcharts.dateFormat('%d/%m/%Y %H:%M', e.min));
              $('#to').val(Highcharts.dateFormat('%d/%m/%Y %H:%M', e.max));
            }
          }
        },

        yAxis: {
          type: 'logarithmic',
          minorTickInterval: 0,
          gridLineWidth: 0,
          labels: {
            enabled: false
          }
        },

        rangeSelector: {
          selected: 0,
          buttons: [{
            type: 'all',
            text: 'All'
          }, {
            type: 'day',
            count: 30,
            text: '30 days'
          }, {
            type: 'day',
            count: 7,
            text: '7 days'
          }, {
            type: 'day',
            count: 1,
            text: '24 h'
          }, {
            type: 'minute',
            count: 60,
            text: '60 min'
          }],
          buttonPosition: {
            x: -2,
            y: 95
          },
          buttonTheme: {
            fill: 'none',
            stroke: 'none',
            width: null,
            style: {
              color: '#FFFFFF',
              fontSize: 11,
              fontWeight: 300,
              textTransform: 'uppercase',
            },
            states: {
              hover: {
                fill: 'none',
                style: {
                  color: '#7BC876'
                }
              },
              select: {
                fill: 'none',
                style: {
                  color: '#7BC876',
                  fontWeight: 300,
                }
              },
              disabled: {
                style: {
                  color: '#888888',
                  cursor: 'default'
                }
              }
            }
          }
        },

        navigator: {
          height: 80,
          maskFill: 'rgba(77, 89, 103, 0.2)',
          outlineColor: "#4D5967",
          handles: {
            backgroundColor: "#4D5967",
            borderColor: "#272A2F"
          },
          series: {
            type: "column",
            color: '#7BC876'
          },
          xAxis: {
            lineWidth: 1,
            lineColor: "#4D5967",
            gridLineWidth: 0,
            labels: {
              enabled: false
            }
          }
        },

        series: [{
          type: 'column',
            data: counts
        }]
      });
    },


    /*
     * Return empty filter object
     */
    getEmptyFilterObject: function() {
      return {
        status: [],
        extra: [],
        time: '',
        author: []
      };
    },


    /*
     * Make sure filter toolbar is always visible
     */
    positionFilterToolbar: function() {
      var menu = $('#filter .menu'),
          scrollbarVisible = menu[0].scrollHeight > (menu.height()),
          toolbarVisible = $('#filter .selected').length > 0;

      $('#filter').toggleClass('fixed', scrollbarVisible && toolbarVisible);
    },


    /*
     * Set filter value to HTML and mark selected filters
     *
     * filter: object with properties for each filter type
     */
    updateFilterUI: function(filter) {
      filter = filter || this.getFilter();

      var placeholder = [],
          selectorType = 'all',
          self = this;

      $('#filter').data('current-filter', filter);

      // Reset all filters
      this.clearSelectedFilters();

      function markSelectedFilters(type) {
        for (var i=0, l=filter[type].length; i < l; i++) {
          var node = $('#filter .menu [data-type="' + filter[type][i] + '"]'),
              title = node.find('.title').text();

          node.addClass('selected');

          if (type === 'author') {
            title = node.find('.name').text() + "'s translations";
          }
          placeholder.push(title);
        }
      }

      for (var type in filter) {
        if (filter[type] && filter[type] !== []) {
          if (type === 'status' || type === 'extra' || type === 'author') {
            markSelectedFilters(type);

          } else if (type === 'time') {
            var node = $('#filter .menu [data-type="time-range"]');
            node.addClass('selected');
            placeholder.push(node.find('.title').text());
          }
        }
      }

      // Special case: Untranslated filter is a union of missing, fuzzy, and suggested
      if (self.untranslatedFilterApplied(filter.status)) {
        $('#filter .menu [data-type="untranslated"]').addClass('selected');
      }

      var selectedCount = $('#filter .selected').length;

      // If only one filter selected, use it's own icon in the filter selector
      if (selectedCount === 1) {
        selectorType = $('#filter .selected').data('type');
        if (selectorType.indexOf('@') !== -1) {
          selectorType = 'author';
        }
      }

      // Update placeholder and filter selector icon
      $('#search').attr('placeholder', 'Search in ' + (placeholder.join(', ') || 'All'));
      $('#filter .button').attr('class', 'button selector ' + selectorType);

      // Update count (N) in Apply N filters button
      $('#filter .toolbar')
        .toggle(selectedCount > 0)
        .find('.variant').toggleClass('plural', selectedCount > 1).end()
        .find('.applied-count').html(selectedCount);

      this.positionFilterToolbar();
    },


    /*
     * Validate Time range input field
     */
    validateTimeRangeInput: function() {
      var from = this.local2server($('#from').val()),
          to = this.local2server($('#to').val());

      if (from && to) {
        return from + '-' + to;
      } else {
        $('#from').toggleClass('error', !from);
        $('#to').toggleClass('error', !to);
        return '';
      }
    },


    /*
     * Validate Time range URL parameter
     */
    validateTimeRangeURL: function (filter) {
      var time = filter.time;

      if (/^[0-9]{12}-[0-9]{12}$/.test(time)) {
        // Populate from/to inputs (needed if filter specified in URL)
        var from = new Date(
          time.substring(0, 4) + '/' +
          time.substring(4, 6) + '/' +
          time.substring(6, 8) + ' ' +
          time.substring(8, 10) + ':' +
          time.substring(10, 12) + ' UTC'
        );

        var to = new Date(
          time.substring(13, 17) + '/' +
          time.substring(17, 19) + '/' +
          time.substring(19, 21) + ' ' +
          time.substring(21, 23) + ':' +
          time.substring(23, 25) + ' UTC'
        );

        if (from != 'Invalid Date' && to != 'Invalid Date') {
          $('#from').val(this.server2local(from));
          $('#to').val(this.server2local(to));

          // Firefox gracefully parses dates, arithmetically converting to meaningful values,
          // so we need to reset the filter in the URL.
          filter.time = this.local2server($('#from').val()) + '-' + this.local2server($('#to').val());

        } else {
          this.resetTimeRange();
        }
      }
    },


    /*
     * Clear selected filters
     */
    clearSelectedFilters: function() {
      $('#filter .selected').removeClass('selected');
    },


    /*
     * Apply selected filters
     */
    applySelectedFilters: function() {
      this.searchEntities();
      $('#filter .selector').click();
    },


    /*
     * Return an array of untranslated filter statuses
     */
    getUntranslatedFilters: function() {
      return ['missing', 'fuzzy', 'suggested'];
    },


    /*
     * Apply untranslated filter
     */
    applyUntranslatedFilter: function(status) {
      var values = this.getUntranslatedFilters();
      for (var i=0, l=values.length; i<l; i++) {
        if (status.indexOf(values[i]) === -1) {
          status.push(values[i]);
        }
      }
    },


    /*
     * Check if untranslated filter applied
     */
    untranslatedFilterApplied: function(status) {
      var values = this.getUntranslatedFilters();
      for (var i=0, l=values.length; i<l; i++) {
        if (status.indexOf(values[i]) === -1) {
          return false;
        }
      }
      return true;
    },


    attachEntityListHandlers: function() {
      var self = this;

      function isExtraFilter(el) {
        return el.hasClass('untranslated') ||
               el.hasClass('unchanged') ||
               el.hasClass('has-suggestions') ||
               el.hasClass('rejected');
      }

      // Filter entities by multiple filters
      $('#filter').on('click', 'li[data-type]:not(".editing"):not(".all") .status', function(e) {
        e.stopPropagation();

        var el = $(this).parents('li'),
            value = el.data('type'),
            filter = self.getFilter(),
            num = -1;

        function updateFilterValue(type) {
          num = filter[type].indexOf(value);
          if (num === -1) {
            filter[type].push(value);
          } else {
            filter[type].splice(num, 1);
          }
        }

        if (el.hasClass('time-range')) {
          filter.time = el.hasClass('selected') ? '' : self.validateTimeRangeInput();

        } else if (el.hasClass('author')) {
          updateFilterValue('author');

        } else if (isExtraFilter(el)) {
          // Special case: Untranslated filter is a union of missing, fuzzy, and suggested
          if (value === 'untranslated') {
            if (self.untranslatedFilterApplied(filter.status)) {
              filter.status = filter.status.indexOf('translated') !== -1 ? ['translated'] : [];
            } else {
              self.applyUntranslatedFilter(filter.status);
            }

          } else {
            updateFilterValue('extra');
          }

        } else {
          updateFilterValue('status');
        }

        self.updateFilterUI();
      });

      // Filter entities by a single filter
      $('#filter').on('click', 'li[data-type]:not(".editing")', function() {
        var el = $(this),
            value = el.data('type'),
            filter = self.getEmptyFilterObject();

        if (el.hasClass('time-range')) {
          filter.time = self.validateTimeRangeInput();
          if (!filter.time) {
            return;
          }

        } else if (el.hasClass('author')) {
          filter.author.push(value);

        } else if (isExtraFilter(el)) {
          if (value === 'untranslated') {
            self.applyUntranslatedFilter(filter.status);

          } else {
            filter.extra.push(value);
          }

        } else if (!el.hasClass('all')) {
          filter.status.push(value);
        }

        self.updateFilterUI(filter);
        self.applySelectedFilters();
      });

      // Switch between relative and fixed filter toolbar position on window resize
      $(window).resize(function () {
        self.positionFilterToolbar();
      });

      // Clear selected filters
      $('#filter .clear-selected').click(function(e) {
        e.preventDefault();

        self.updateFilterUI(self.getEmptyFilterObject());
        $('#filter .toolbar').hide();
      });

      // Apply selected filters
      $('#filter .apply-selected').click(function(e) {
        e.preventDefault();

        self.applySelectedFilters();
      });

      // Update authors and time range
      $('#filter:not(".opened") .selector').click(function() {
        if ($('#filter').is('.opened')) {
          return;
        }

        // Disable for All Projects for performance reasons
        if (self.project.slug === 'all-projects') {
          self.updateRangePicker([]);
          self.updateAuthors([]);
          return;
        }

        self.NProgressUnbind();

        $.ajax({
          url: '/' + self.locale.code + '/' + self.project.slug + '/' + self.part + '/authors-and-time-range/',
          success: function(data) {
            self.updateRangePicker(data.counts_per_minute);
            self.updateAuthors(data.authors);
          }
        });

        self.NProgressBind();
      });

      // Time range editing toggle
      $('#filter .horizontal-separator .edit').click(function() {
        self.toggleRangeEditing();
      });

      // Initialize date & time range picker
      $('#filter .time-range').on('focusin', 'input:not(".hasDatepicker")', function() {
        $.timepicker.datetimeRange($('#from'), $('#to'), {
          showTime: false,
          showHour: false,
          showMinute: false,
          showButtonPanel: false,
          nextText: '',
          prevText: '',
          dateFormat: 'dd/mm/yy',
          maxDate: new Date()
        });
      });

      // Clear error styling on value change
      $('#filter .time-range input').on('input propertychange change', function() {
        var from = self.local2chart($('#from').val()),
            to = self.local2chart($('#to').val());

        $('#range-picker').highcharts().xAxis[0].setExtremes(from, to);
        $(this).removeClass('error');
      });

      // Do not close the filter menu if clicked inside the menu
      $('#filter').on('click', '.menu', function (e) {
        e.stopPropagation();
      });

      // Do not close the filter menu when navigating calendar
      $('html').on('click', function (e) {
        if ($(e.target).is('#ui-datepicker-div') || $(e.target).is('.ui-icon') || $(e.target).parents('#ui-datepicker-div').length) {
          $('#filter .selector').click();
        }
      });

      // Trigger event with a delay (e.g. to prevent UI blocking)
      // Delay should be called after whole input
      var timer = 0;
      var delay = (function () {
        return function (callback, ms) {
          clearTimeout(timer);
          timer = setTimeout(callback, ms);
        };
      })();

      // Search entities (keyup event also triggered on modifier keys etc.)
      $('#search').off('input').on('input', function () {
        delay(function () {
          self.searchEntities();
        }, 500);
      });

      // Select entities for batch editing
      $('#entitylist').on('click', '.entity > .status:not(".unselectable")', function(e) {
        var entity = $(this).parent('li');
        self.selectEntity(entity, e);
      });

      // Edit selected entities from 1-column layout
      $('#entitylist .batch-bar .edit-all').click(function(e) {
        e.preventDefault();

        $("#entitylist").css('left', -$('#sidebar').width());
        $("#editor").css('left', 0);
      });

      // Scroll entities
      $('#entitylist .wrapper').scroll(function(e) {
        e.preventDefault();

        var $editableEntities = $('#entitylist .wrapper .editables'),
            $uneditableEntities = $('#entitylist .wrapper .uneditables'),
            entitiesHeight = $editableEntities.height() + $uneditableEntities.height(),
            list = $('#entitylist .wrapper');

        // Prevents from firing multiple calls during onscroll event
        if (entitiesHeight > 0 && (list.scrollTop() >= entitiesHeight * 0.75 - list.height()) && self.hasNext && !self.isLoading()) {
          self.loadNextEntities('scroll');
        }
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

      function mouseUpHandler() {
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
     * Is original string pluralized
     */
    isPluralized: function () {
      var original = '',
          nplurals = this.locale.nplurals,
          plural_rule = this.locale.plural_rule,
          pluralForm = this.getPluralForm();

      if ((nplurals < 2 && $('#source-pane').is('.pluralized')) ||
          (nplurals === 2 && pluralForm === 1) ||
          (nplurals > 2 &&
           pluralForm !== -1 &&
           pluralForm !== eval(plural_rule.replace(/n/g, 1)))) {
        original = '_plural';
      }

      return original;
    },


    /*
     * Check if translation length limit exceeded
     */
    translationLengthLimitExceeded: function (translation) {
      return this.translationLengthLimit && this.stripHTML(translation).length > this.translationLengthLimit;
    },


    /*
     * Remove event first to avoid double handling
     */
    reattachSaveButtonHandler: function () {
      $('#save, #save-anyway')
        .off('click.save')
        .on('click.save', this.saveTranslation);
    },


    /*
     * Submit translation to DB
     */
    saveTranslation: function (e) {
      e.preventDefault();
      var self = Pontoon,
          entity = self.getEditorEntity(),
          translation = $('#translation').val();

      // Prevent empty translation submissions if not supported
      if (translation === '' &&
        ['properties', 'ini', 'dtd', 'ftl'].indexOf(entity.format) === -1) {
          self.endLoader('Empty translations cannot be submitted.', 'error');
          return;
      }

      if (self.translationLengthLimitExceeded(translation)) {
        self.endLoader('Translation too long.', 'error');
        return;
      }

      // Prevent double translation submissions
      $(this).off('click.save');

      self.updateOnServer(entity, translation, true);
    },


    /*
     * Restore in-place translation to previous state or original
     * We need to do this to avoid setting empty string
     */
    restoreInPlaceTranslation: function () {
      var entity = this.getEditorEntity();

      if (entity) {
        var translation = entity.translation[0].string || entity.original;
        this.updateInPlaceTranslation(translation);
      }
    },


    /*
     * Update in-place translation if applicable
     */
    updateInPlaceTranslation: function (translation) {
      translation = translation || $('#editor textarea:visible:first').val();
      var entity = this.getEditorEntity(),
          pluralForm = this.getPluralForm(true);

      if (entity.body && pluralForm === 0 && (this.user.canTranslate() || !entity.translation[pluralForm].approved)) {
        this.postMessage("SAVE", {
          translation: translation,
          id: entity.id
        });
      }
    },


    /*
     * Attach event handlers to editor elements
     */
    attachEditorHandlers: function () {
      var self = this;

      // Top bar
      $('#single .topbar > a').click(function (e) {
        e.preventDefault();

        var sec = $(this).attr('id');

        switch (sec) {

        case 'back':
          self.checkUnsavedChanges(function() {
            self.stopInPlaceEditing();
            self.goBackToEntityList();
          });
          break;

        case 'previous':
          self.navigateToEntity('previous');
          break;

        case 'next':
          self.navigateToEntity('next');
          break;

        }
      });

      // Zoom in screenshot
      $('#screenshots').on('click', 'img', function () {
        $('body').append('<div id="overlay">' + this.outerHTML + '</div>');
        $('#overlay').fadeIn('fast');
      });

      // Close zoomed screenshot
      $('body').on('click', '#overlay', function() {
        $(this).fadeOut('fast', function() {
          $(this).remove();
        });
      });

      // Load Resource
      $('body').on('click', '#metadata a.resource-path', function(e) {
        e.preventDefault();
        self.jumpToPart($(this).html());
      });

      // Insert placeable at cursor, replace selection or at the end if not focused
      // Use mousedown instead of click to be able to detect the last focused textarea
      $('#source-pane').on('mousedown', '.placeable', function (e) {
        e.preventDefault();

        // Ignore for anonymous users
        if (!self.user.id) {
          return;
        }

        var textarea = $('#editor textarea:visible:focus, #editor textarea:visible:first'),
            selectionStart = textarea.prop('selectionStart'),
            selectionEnd = textarea.prop('selectionEnd'),
            placeable = $(this).text(),
            cursorPos = selectionStart + placeable.length,
            before = textarea.val(),
            after = before.substring(0, selectionStart) + placeable + before.substring(selectionEnd);

        textarea.val(after).focus();
        textarea[0].setSelectionRange(cursorPos, cursorPos);
        self.updateCurrentTranslationLength();
        self.updateInPlaceTranslation();
      });

      function switchToPluralForm(tab) {
        $("#plural-tabs li").removeClass('active');
        tab.addClass('active');

        var entity = self.getEditorEntity(),
            i = tab.index(),
            original = entity['original' + self.isPluralized()],
            marked = entity['marked' + self.isPluralized()],
            title = !self.isPluralized() ? 'Singular' : 'Plural',
            source = entity.translation[i].string;

        $('#source-pane h2').html(title).show();
        $('#original').html(marked);

        self.updateAndFocusTranslationEditor(source);
        $('#translation-length .original-length').html(original.length);
        self.moveCursorToBeginning();
        self.updateCurrentTranslationLength();
        self.updateCachedTranslation();

        $('#quality:visible .cancel').click();
        self.updateHelpers();
      }

      // Plurals navigation
      $('#plural-tabs a').click(function (e) {
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

      /* Translate textarea and FTL area keyboard shortcuts
       *
       * Known keyboard shortcut clashes:
       * - Czech Windows keyboard: Ctrl + Alt + C/F/./,
       * - Polish keyboard: Alt + C
       */
      $('#editor').on('keydown', 'textarea', function (e) {
        var key = e.which;

        // Prevent triggering unnecessary events in 1-column layout
        if (!$("#editor").is('.opened')) {
          return false;
        }

        // Enter: Save translation
        if (key === 13 && !e.shiftKey && !e.altKey) {
          if ($('#leave-anyway').is(':visible')) {
            $('#leave-anyway').click();
          } else {
            self.saveTranslation(e);
          }
          return false;
        }

        // Esc: Cancel translation and return to entity list
        if (key === 27) {
          if ($('.warning-overlay').is(':visible')) {
            $('.warning-overlay .cancel').click();
          } else if (!self.app.advanced) {
            self.checkUnsavedChanges(function() {
              self.stopInPlaceEditing();
              self.goBackToEntityList();
            });
          }
          return false;
        }

        // Ctrl + Shift + C: Copy from source
        if (e.ctrlKey && e.shiftKey && key === 67) {
          $('#copy').click();
          return false;
        }

        // Ctrl + Shift + Backspace: Clear translation
        if (e.ctrlKey && e.shiftKey && key === 8) {
          $('#clear').click();
          return false;
        }

        // Tab: Select suggestions
        if (!$('.menu').is(':visible') && key === 9 && !e.ctrlKey) {

          // Rich FTL editor with complex message: ignore tab key
          if (self.fluent.isFTLEditorEnabled() && self.fluent.isComplexFTL()) {
            return;
          }

          // Source FTL editor: insert tab character
          if (self.fluent.isSourceFTLEditorEnabled()) {
            e.preventDefault();

            var textarea = $('#translation')[0];
            var oldStart = textarea.selectionStart;
            var start = textarea.value.substring(0, textarea.selectionStart);
            var end = textarea.value.substring(textarea.selectionEnd);

            textarea.value = start + '\t' + end;
            textarea.selectionEnd = oldStart + 1;

            return;
          }

          var section = $('#helpers section:visible'),
              index = section.find('li.suggestion.hover').index() + 1;

          // If possible, select next suggestion, or select first
          if (section.find('li.suggestion:last').is('.hover')) {
            index = 0;
          }

          section
            .find('li.suggestion').removeClass('hover').end()
            .find('li.suggestion:eq(' + index + ')').addClass('hover').click();

          self.updateScroll(section);
          return false;
        }

      // Update length (keydown is triggered too early)
      }).unbind("input propertychange").bind("input propertychange", function () {
        self.updateCurrentTranslationLength();
        self.updateInPlaceTranslation();
        $('.warning-overlay:visible .cancel').click();
      });

      // Close warning box
      $('.warning-overlay .cancel').click(function (e) {
        e.preventDefault();

        $('.warning-overlay')
          .find('ul').empty().end()
        .hide();

        $('#translation').focus();
      });

      $('#leave-anyway').click(function() {
        var callback = self.checkUnsavedChangesCallback;
        if (callback) {
          self.restoreInPlaceTranslation(); // Before callback, so that entity is available!
          callback();
          $('#unsaved').hide();
          $('#translation').val(self.cachedTranslation);
        }
      });

      // Copy source to translation
      $('#copy').click(function (e) {
        e.preventDefault();

        var entity = self.getEditorEntity(),
            original = entity['original' + self.isPluralized()],
            source = self.fluent.getSourceStringValue(entity, original);

        self.updateAndFocusTranslationEditor(source);
        self.moveCursorToBeginning();
        self.updateCurrentTranslationLength();
        self.updateInPlaceTranslation();
      });

      // Clear translation area
      $('#clear').click(function (e) {
        e.preventDefault();

        // FTL Editor
        if (self.fluent.isFTLEditorEnabled()) {
          self.fluent.renderEditor({
            pk: null,
            string: ''
          });

        // Standard Editor
        } else {
          self.updateAndFocusTranslationEditor('');
          self.moveCursorToBeginning();
          self.updateCurrentTranslationLength();
          self.updateInPlaceTranslation();
        }
      });

      // Save translation
      $('#save, #save-anyway').on('click.save', self.saveTranslation);

      // Custom search: trigger with Enter
      $('#helpers .machinery input').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
        if (e.which === 13) {
          var source = $(this).val(),
              entity = self.getEditorEntity();

          // Reset to original string on empty search
          if (!source) {
            source = entity['original' + self.isPluralized()];
          }

          if (self.machinerySource !== source) {
            self.getMachinery(source);
            self.machinerySource = source;
          }
          return false;
        }
      });

      // Copy helpers result to translation
      $('#helpers section').on('click', 'li:not(".disabled")', function (e) {
        var source = $(this).find('.translation-clipboard').text();

        // Ignore clicks on links and buttons
        if ($(e.target).closest('a, menu button').length) {
          return;
        }

        // Ignore for anonymous users
        if (!self.user.id) {
          return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
          return;
        }

        // FTL Editor
        if (self.fluent.isFTLEditorEnabled() && !$('#helpers .machinery').is(':visible')) {
          self.fluent.renderEditor({
            pk: true,
            string: source
          });

        // Standard Editor
        } else {
          self.updateAndFocusTranslationEditor(source);
          self.moveCursorToBeginning();
          self.updateCurrentTranslationLength();
          self.updateInPlaceTranslation();
        }

        $('.warning-overlay:visible .cancel').click();
      });

      // Approve and delete translations
      $('#helpers .history').on('click', 'menu .approve', function () {
        $(this).parents('li').click();

        var entity = self.getEditorEntity(),
            translation = $('#translation').val();

        if (self.translationLengthLimitExceeded(translation)) {
          self.endLoader('Translation too long.', 'error');
          return;
        }

        // Mark that user approved translation instead of submitting it
        self.approvedNotSubmitted = true;
        self.updateOnServer(entity, translation, true);
      });

      $('#helpers .history').on('click', 'menu .unapprove', function () {
        var button = $(this),
            translationId = parseInt($(this).parents('li').data('id'));

        $.post('/unapprove-translation/', {
          csrfmiddlewaretoken: $('#server').data('csrf'),
          translation: translationId,
          paths: self.getPartPaths(self.currentPart)
        }).then(function(data) {
          var entity = self.getEditorEntity(),
              pf = self.getPluralForm(true);

          self.stats = data.stats;

          self.updateTranslation(entity, pf, data.translation);

          // FTL Editor
          if (self.fluent.isFTLEditorEnabled()) {
            self.fluent.renderEditor(data.translation);

          // Standard Editor
          } else {
            self.updateAndFocusTranslationEditor(data.translation.string);
            self.updateCachedTranslation();
            self.updateCurrentTranslationLength();
          }

          if (entity.body && pf === 0) {
            self.postMessage("SAVE", {
              translation: data.translation.string,
              id: entity.id
            });
          }

          button.removeClass('unapprove').addClass('approve');
          button.prop('title', 'Approve');
          button.parents('li.translated').removeClass('translated').addClass('suggested');
          button.parents('li').find('.info a').prop('title', self.getApproveButtonTitle({
            approved: false,
            unapproved_user: self.user.display_name
          }));

          self.endLoader('Translation unapproved');
        }, function() {
          self.endLoader("Couldn't unapprove this translation.");
        });
      });

      $('#helpers .history').on('click', 'menu .reject', function () {
        var button = $(this);
        // Reject a translation.
        $.ajax({
          url: '/reject-translation/',
          type: 'POST',
          data: {
            csrfmiddlewaretoken: $('#server').data('csrf'),
            translation: $(this).parents('li').data('id'),
            paths: self.getPartPaths(self.currentPart)
          },
          success: function(data) {
            var entity = self.getEditorEntity();
            var pf = self.getPluralForm(true);

            self.stats = data.stats;

            self.updateTranslation(entity, pf, data.translation);

            var item = button.parents('li');
            item.addClass('rejected').removeClass('translated suggested fuzzy');
            item.find('.unapprove').removeClass('unapprove').addClass('approve').prop('title', 'Approve');
            button.addClass('unreject').removeClass('reject').prop('title', 'Unreject');

            self.endLoader('Translation rejected');
          },
          error: function() {
            self.endLoader('Oops, something went wrong.', 'error');
          }
        });
      });

      $('#helpers .history').on('click', 'menu .unreject', function () {
        var button = $(this),
            translationId = parseInt($(this).parents('li').data('id'));

        $.post('/unreject-translation/', {
          csrfmiddlewaretoken: $('#server').data('csrf'),
          translation: translationId,
          paths: self.getPartPaths(self.currentPart)
        }).then(function(data) {
          var entity = self.getEditorEntity();
          var pf = self.getPluralForm(true);

          self.stats = data.stats;

          self.updateTranslation(entity, pf, data.translation);

          // FTL Editor
          if (self.fluent.isFTLEditorEnabled()) {
            self.fluent.renderEditor(data.translation);

          // Standard Editor
          } else {
            self.updateAndFocusTranslationEditor(data.translation.string);
            self.updateCachedTranslation();
            self.updateCurrentTranslationLength();
          }

          if (entity.body && pf === 0) {
            self.postMessage("SAVE", {
              translation: data.translation.string,
              id: entity.id
            });
          }

          button.removeClass('unreject').addClass('reject');
          button.prop('title', 'Reject');
          button.parents('li.rejected').removeClass('rejected').addClass('suggested');
          button.parents('li').find('.info a').prop('title', self.getApproveButtonTitle({
            rejected: false,
            unrejected_user: self.user.display_name
          }));

          self.endLoader('Translation unrejected');
        }, function() {
          self.endLoader("Couldn't unreject this translation.");
        });
      });

      // Toggle suggestion diff
      $('#helpers .history').on('click', '.toggle-diff', function (e) {
        e.preventDefault();

        var oldText = $(this).html();
        $(this).html($(this).data('alternative-text'));
        $(this).data('alternative-text', oldText);
        $(this).parents('li').find('.translation, .translation-diff').toggle();
      });
    },


    /*
     * Select all strings
     */
    selectAllEntities: function () {
      var self = this;

      self.allEntitiesSelected = true;
      $('#entitylist .entity:visible').addClass('selected');

      self.selectedEntities = [];
      self.openBatchEditor(true);

      this.getEntities({pk_only: true}).then(function(data) {
        var locallySelectedEntities = self.getEntitiesIds('#entitylist .entity:visible.selected'),
            mergedEntities = data.entity_pks.concat(locallySelectedEntities),
            uniqueEntities = self.removeDuplicates(mergedEntities);

        self.selectedEntities = uniqueEntities;
        self.openBatchEditor();
      });
    },


    /*
     * Attach event handlers to batch editor elements
     */
    attachBatchEditorHandlers: function () {
      var self = this;

      // Clear selection
      $('#sidebar .quit-batch-editing').click(function (e) {
        e.preventDefault();

        if (self.app.advanced) {
          self.openFirstEntity();
        } else {
          self.goBackToEntityList();
        }
      });

      // Select All
      $('#sidebar .select-all').click(function (e) {
        e.preventDefault();

        self.selectAllEntities();
      });

      // Actions
      $('#approve-all, #reject-all, #replace-all').click(function(e) {
        e.preventDefault();

        var button = this,
            action = $(this).attr('id').split('-')[0],
            find = $('#batch .find').val(),
            replace = $('#batch .replace').val(),
            message = '';

        // Disable before request complete
        if ($(button).is('.loading')) {
          return;
        }

        clearTimeout(self.batchButttonTimer);

        // Delete check
        if ($(button).is('#reject-all')) {
          if ($(button).is('.confirmed')) {
            $(button).removeClass('confirmed show-message');

          } else {
            $(button)
              .addClass('confirmed show-message')
              .find('.message').html('Are you sure?');
            return;
          }
        }

        // Find and Replace validation
        if (action === 'replace') {
          if (find === '') {
            return $('#batch .find').focus();
          }

          if (find === replace) {
            return $('#batch .replace').focus();
          }
        }

        $(button).addClass('loading');

        self.waitForAttribute('selectedEntities').then(function() {
          $.ajax({
            url: '/batch-edit-translations/',
            type: 'POST',
            data: {
              csrfmiddlewaretoken: $('#server').data('csrf'),
              locale: self.locale.code,
              action: action,
              entities: self.selectedEntities.join(','),
              find: find,
              replace: replace
            },
            success: function(data) {
              if ('count' in data) {
                var itemsText = data.count === 1 ? 'string' : 'strings';
                var actionText = action + 'd';

                if (action === 'reject') {
                  itemsText = 'suggestion' + (data.count === 1 ? '' : 's');
                  actionText = 'rejected';
                }

                message = data.count + ' ' + itemsText + ' ' + actionText;

                // Update UI (entity list, progress, in-place)
                if (data.count > 0) {
                  var checkedEntities = self.getEntitiesIds('#entitylist .entity.selected');
                  self.getEntities({entity_ids: checkedEntities.join(',')}).then(function(entitiesData) {
                    self.stats = entitiesData.stats;
                    self.updateFilterUI();

                    var entitiesMap = {};
                    $.each(entitiesData.entities, function() {
                      entitiesMap[this.pk] = this;
                    });

                    $('#entitylist .entity.selected').each(function() {
                      var entity = this.entity,
                          updatedEntity = self.getEntityById(entity.pk, entitiesData.entities);

                      if (updatedEntity) {
                        entity.translation = updatedEntity.translation;
                        self.updateEntityUI(entity);

                        if (entity.body) {
                          if ($(button).is('#reject-all') && !entity.translation[0].pk) {
                            self.postMessage("DELETE", {
                              id: entity.id
                            });
                          } else {
                            self.postMessage("SAVE", {
                              translation: entity.translation[0].string,
                              id: entity.id
                            });
                          }
                        }
                      }
                    });
                  });
                }

              // Empty translations produced by replace might not be always allowed
              } else if (data.error) {
                message = data.error;
                $('#batch .replace').focus();
              }
            },
            error: function() {
              message = 'Oops, something went wrong';
            },
            complete: function() {
              $(button)
                .toggleClass('loading')
                .addClass('show-message')
                .find('.message').html(message);

              // Reset button
              self.batchButttonTimer = setTimeout(function() {
                $(button).removeClass('show-message');
              }, 3000);
            }
          });
        });
      });

      // Keyboard shortcuts
      $('#batch .find-replace input').unbind('keydown.pontoon').bind('keydown.pontoon', function (e) {
        var key = e.which;

        // Enter: confirm
        if (key === 13) {
          $('#replace-all').click();
          return false;
        }
      });
    },


    /*
     * Update progress indicator and value
     *
     * entity If provided, also update the parts menu
     */
    updateProgress: function (entity) {
      var self = this,
          stats = self.stats,
          total = stats.total,
          suggested = stats.translated,
          translated = stats.approved,
          fuzzy = stats.fuzzy,
          missing = total - suggested - translated - fuzzy,
          fraction = {
            translated: total ? translated / total : 0,
            suggested: total ? suggested / total : 0,
            fuzzy: total ? fuzzy / total : 0,
            missing: total ? missing / total : 0
          },
          number = Math.floor(fraction.translated * 100),
          translatedOld = parseInt($('#progress .menu .details .translated p').html().replace(/,/g, ''));

      // Update graph
      $('#progress .graph').each(function() {
        var context = this.getContext('2d');
        // Clear old canvas content to avoid aliasing
        context.clearRect(0, 0, this.width, this.height);
        context.lineWidth = 3;

        var x = this.width/2,
            y = this.height/2,
            radius = (this.width - context.lineWidth)/2,
            end = null;

        $('#progress .details > div').each(function() {
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

      // Update graph legend
      $('#progress .menu').find('header span').html(self.numberWithCommas(total)).end()
        .find('.details')
          .find('.translated p').html(self.numberWithCommas(translated)).end()
          .find('.suggested p').html(self.numberWithCommas(suggested)).end()
          .find('.fuzzy p').html(self.numberWithCommas(fuzzy)).end()
          .find('.missing p').html(self.numberWithCommas(missing));

      // Update filter
      $('#filter .menu')
          .find('.all .count').html(self.numberWithCommas(total)).end()
          .find('.translated .count').html(self.numberWithCommas(translated)).end()
          .find('.suggested .count').html(self.numberWithCommas(suggested)).end()
          .find('.fuzzy .count').html(self.numberWithCommas(fuzzy)).end()
          .find('.missing .count').html(self.numberWithCommas(missing));

      // Update parts menu
      if (entity && total) {
        var paths = [],
            parts = $('.project .menu .name[data-slug=' + self.project.slug + ']')
                      .data('parts')[self.locale.code];

        $(parts).each(function() {
          paths = self.getPartPaths(this);

          if (paths.indexOf(entity.path) !== -1) {
            this.approved_strings += (translated - translatedOld);
          }
        });
      }

      $('#progress').show();
    },


    /*
     * Update entity in the entity list
     *
     * entity Entity
     */
    updateEntityUI: function (entity) {
      var self = this,
          status = self.getEntityStatus(entity),
          translation = entity.translation[0],
          translationString = translation.string || '';

      translationString = self.fluent.getSimplePreview(translation, translationString, entity);

      entity.ui
        .removeClass('translated suggested fuzzy missing partial')
        .addClass(status)
        .find('.translation-string')
          .html(self.markPlaceables(translationString));

      self.updateProgress(entity);
    },


    /*
     * Update translation object with provided data
     *
     * entity Entity to update Translation for
     * pluralForm Translation plural form to update
     * data Data to update translation with
     */
    updateTranslation: function (entity, pluralForm, data) {
      for (var key in data) {
        entity.translation[pluralForm][key] = data[key];
      }

      // TODO: update editor/entitylist on delete and copy from helpers
      this.updateEntityUI(entity);
    },


    /*
     * Update all translations in localStorage on server
     */
    syncLocalStorageOnServer: function() {
      if (! (localStorage instanceof Storage) || localStorage.length === 0) {
        return;
      }

      var len = this.entities.length;
      for (var i = 0; i < len; i++) {
        var entity = this.entities[i],
            key = this.getLocalStorageKey(entity),
            value = localStorage[key];
        if (value) {
          value = JSON.parse(localStorage[key]);
          this.updateOnServer(entity, value.translation, false);
          delete localStorage[key];
        }
      }

      // Clear all other translations
      localStorage.clear();
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
     * syncLocalStorage Synchronize translations in localStorage with the server
     */
    updateOnServer: function (entity, translation, syncLocalStorage) {
      var self = this,
          pluralForm = self.getPluralForm();

      function goToNextTranslation() {
        // Quit
        if (!$('#editor:visible').is('.opened')) {
          return;

        // Go to next plural form
        } else if (pluralForm !== -1 && $("#editor").is('.opened')) {
          var next = $('#plural-tabs li:visible')
            .eq(pluralForm + 1).find('a');

          if (next.length === 0) {
            self.navigateToEntity('next');
          } else {
            next.click();
          }

        // Go to next entity
        } else {
          self.navigateToEntity('next');
        }
      }

      function renderTranslation(data) {
        self.stats = data.stats;

        if (data.type) {
          self.endLoader('Translation ' + data.type);

          if (self.approvedNotSubmitted) {
            $('#helpers .history [data-id="' + data.translation.pk + '"] button.approve')
              .parents('li').addClass('approved')
                .siblings().removeClass('approved');
          }

          var pf = self.getPluralForm(true);
          self.cachedTranslation = self.fluent.getTranslationSource();
          self.updateTranslation(entity, pf, data.translation);
          self.updateInPlaceTranslation(data.translation.string);
          self.updateFilterUI();

          // Update translation, including in place if possible
          if (entity.body && (self.user.canTranslate() || !entity.translation[pf].approved)) {
            self.postMessage("SAVE", {
              translation: translation,
              id: entity.id
            });
          }

          goToNextTranslation();

        } else if (data.warnings) {
          self.endLoader();
          self.showQualityCheckWarnings(data.warnings);

        } else if (data.same) {
          self.endLoader(data.message, 'error');
          goToNextTranslation();

        } else {
          self.endLoader(data, 'error');
        }

        if (!data.warnings) {
          self.approvedNotSubmitted = null;
        }
      }

      // If the entity has a plural string, but the locale has nplurals == 1,
      // then pluralForm is -1 and needs to be normalized to 0 so that it is
      // stored in the database as a pluralized string.
      // TODO: Get a better flag for pluralized strings than original_plural.
      var submittedPluralForm = pluralForm;
      if (entity.original_plural && submittedPluralForm === -1) {
        submittedPluralForm = 0;
      }

      if (self.XHRupdateOnServer) {
        self.XHRupdateOnServer.abort();
      }

      // If Fluent translation contains error, display it and abort
      var serializedTranslation = self.fluent.serializeTranslation(entity, translation);
      if (serializedTranslation.error) {
        self.endLoader(serializedTranslation.error, 'error', 5000);
        return self.reattachSaveButtonHandler();
      }

      self.XHRupdateOnServer = $.ajax({
        url: '/update/',
        type: 'POST',
        data: {
          csrfmiddlewaretoken: $('#server').data('csrf'),
          locale: self.locale.code,
          entity: entity.pk,
          translation: serializedTranslation,
          plural_form: submittedPluralForm,
          original: entity['original' + self.isPluralized()],
          ignore_check: $('#quality').is(':visible') || !syncLocalStorage || entity.format === 'ftl',
          approve: self.approvedNotSubmitted || false,
          paths: self.getPartPaths(self.currentPart),
          force_suggestions: self.user.forceSuggestions
        },
        success: function(data) {
          renderTranslation(data);
          // Connection exists -> sync localStorage
          if (syncLocalStorage) {
            self.syncLocalStorageOnServer();
          }
        },
        error: function(error) {
          // Skip if other request in progress
          if (self.XHRupdateOnServer && self.XHRupdateOnServer.statusText === 'abort') {
            return;
          }

          if (error.status === 0) {
            // No connection -> use offline mode
            self.addToLocalStorage(entity, translation);
            // Imitate data to add translation
            var data = {
              type: "added",
              translation: {
                approved: self.user.canTranslate(),
                fuzzy: false,
                string: translation
              }
            };
            renderTranslation(data);
          } else {
            self.endLoader('Oops, something went wrong.', 'error');
            self.approvedNotSubmitted = null;
          }
        },
        complete: function() {
          self.reattachSaveButtonHandler();
        }
      });
    },


    /*
     * Update part selector
     *
     * title Part title
     */
    updatePartSelector: function (title) {
      if (title === 'all-resources') {
        title = 'All Resources';
      }
      $('.part .selector')
        .attr('title', title)
        .find('.title')
          // Only show filename instead of full path
          .html(title.replace(/^.*[/]/, ''));
    },


    /*
     * Update download/upload form fields with translation project data
     */
    updateFormFields: function (form) {
      var self = this,
          slug = self.project.slug,
          code = self.locale.code,
          part = self.part;

      // Use first part when translating All Resources
      if (part === 'all-resources') {
        part = self.getProjectData('parts')[code][0].title;
      }

      form
        .find('#id_slug').val(slug).end()
        .find('#id_code').val(code).end()
        .find('#id_part').val(part);
    },


    /*
     * Mark Go button as active if main menu doesn't fully resemble
     * locale, project, part combination currently being translated
     */
    updateGoButton: function () {
      var toggle = this.getSelectedLocale() !== this.locale.code ||
                   this.getSelectedProject() !== this.project.slug ||
                   this.getSelectedPart() !== this.currentPart.title;
      $('#go').toggleClass('active', toggle);
    },


    /*
     * Update project and (if needed) part menu
     */
    updateProjectMenu: function () {
      var projects = this.getLocaleData('projects'),
          slug = this.getProjectData('slug');

      // Fallback if selected project not available for the selected locale
      if (projects.indexOf(slug) === -1) {
        slug = projects.sort()[0];
      }

      // Make sure part menu is always updated
      $('.project .menu [data-slug="' + slug + '"]').parent().click();

      // Update All Projects menu entry parts
      var parts = {};
      parts[this.getSelectedLocale()] = [{
        title: 'all-resources',
        resource__path: []
      }];
      $('.project .menu .all-projects .name').data('parts', parts);

      this.updateGoButton();
    },


    /*
     * Update part menu
     */
    updatePartMenu: function () {
      var locale = this.getSelectedLocale(),
          project = this.getSelectedProject(),
          parts = this.getProjectData('parts')[locale],
          currentPart = this.getSelectedPart(),
          part = $.grep(parts, function (e) { return e.title === currentPart; });

      // Fallback if selected part not available for the selected locale & project
      if (!part.length) {
        this.updatePartSelector(parts[0].title);
      }

      // Hide part menu for All Projects
      $('.part.select').toggleClass('hidden', project === 'all-projects');

      this.updateGoButton();
    },


    /*
     * Checks whether we should focus iframe on hover
     */
    isIframeHoverIntentional: function () {
      return (!this.dragging && !$('.menu').is(':visible'));
    },


    /*
     * Attach event handlers to main toolbar elements
     */
    attachMainHandlers: function () {
      var self = this;

      // Main keyboard shortcuts
      $('html').on('keydown', function (e) {
        var key = e.which;

        // Alt + Down: Go to next string
        if (e.altKey && key === 40) {
          self.navigateToEntity('next');
          return false;
        }

        // Alt + Up: Go to previous string
        if (e.altKey && key === 38) {
          self.navigateToEntity('previous');
          return false;
        }
      });

      // iFrame fix on hiding menus
      $('body').bind("click.main", function () {
        $('#iframe-cover').hide();
      });

      // Locale menu handler
      $('.locale .menu li:not(".no-match")').click(function () {
        var menuItem = $(this),
            locale = menuItem.find('.language').data('code'),
            language = menuItem.find('.language').html();

        $('.locale .selector')
          .find('.language')
            .html(language)
            .data('code', locale)
          .end()
          .find('.code').html(locale);

        if (!self.getLocaleData('projects')) {
          $.ajax({
            url: '/teams/' + locale + '/projects/',
            success: function(projects) {
              menuItem.find('.language').data('projects', projects);
              self.updateProjectMenu();
            }
          });

        } else {
          self.updateProjectMenu();
        }
      });

      // Show only projects available for the selected locale
      $('.project .selector').click(function () {
        var projects = Pontoon.getLocaleData('projects'),
            $menu = $(this).parents('.select').find('.menu');

        // Hide all projects
        $menu.find('li')
          .toggleClass('limited', false)
          .toggle(false);

        // Show requested projects
        $(projects).each(function() {
          $menu
              .find('.name[data-slug="' + this + '"]')
            .parent()
              .toggleClass('limited', true)
              .toggle(true);
        });
      });

      // Project menu handler
      $('.project .menu li:not(".no-match"), .static-links .all-projects').click(function () {
        var project = $(this).find('.name'),
            name = project.html(),
            slug = project.data('slug'),
            locale = self.getSelectedLocale();

        // Select project
        if (!$('.project .menu .search-wrapper > a').is('.back:visible')) {
          $('.project .selector .title')
            .html(name)
            .data('slug', slug);

          var projectParts = project.data('parts');

          if (projectParts && projectParts[locale]) {
            self.updatePartMenu();

          } else {
            var url;
            if (slug !== 'all-projects') {
              url = '/' + locale + '/' + slug + '/parts/';
            } else {
              url = '/teams/' + locale + '/stats/';
            }

            $.ajax({
              url: url,
              success: function(parts) {
                if (projectParts) {
                  projectParts[locale] = parts;
                } else {
                  var obj = {};
                  obj[locale] = parts;
                  project.data('parts', obj);
                }
                self.updatePartMenu();
              }
            });
          }
        }
      });

      // Show only parts available for the selected project
      $('.part .selector').click(function () {
        var locale = self.getSelectedLocale(),
            parts = self.getProjectData('parts')[locale],
            menu = $(this).siblings('.menu').find('ul'),
            currentProject = self.getProjectData('slug') === self.project.slug,
            currentLocale = self.getLocaleData('code') === self.locale.code;

        menu.find('li:not(".no-match")').remove();
        $(parts).each(function(i) {
          var cls = '',
              title = this.title,
              percent = '0%';

          if (currentProject && currentLocale && self.part === title) {
            cls = ' class="current"';
          }

          if (this.resource__total_strings > 0) {
            percent = Math.floor(this.approved_strings / this.resource__total_strings * 100) + '%';
          }

          if (i < parts.length - 1) {
            menu.append('<li' + cls + '>' +
              '<span>' + title + '</span>' +
              '<span>' + percent + '</span>' +
            '</li>');

          } else {
            menu.parents('.menu').find('.static-links')
              .find('.percent').html(percent).end()
              .find('.all-resources').toggleClass('current', self.part === 'all-resources');
          }
        });
      });

      // Parts menu handler
      $('.part .menu').on('click', 'li:not(".no-match"), .static-links .all-resources', function () {
        var title = $(this).find('span:first').html();
        self.updatePartSelector(title);
        self.updateGoButton();
      });

      // Open selected project (part) and locale combination
      $('#go').click(function (e) {
        e.preventDefault();
        self.jumpToPart(self.getSelectedPart());

        self.closeNotification();
      });

      // Close notification on click
      $('body > header').on('click', '.notification', function() {
        Pontoon.closeNotification();
      });

      // File upload
      $('#id_uploadfile').change(function() {
        self.updateFormFields($('form#upload-file'));
        $('form#upload-file').submit();
      });

      // Focus & unfocus iframe to make history (back/forward) work
      $('#source, #iframe-cover').hover(function() {
        if (self.isIframeHoverIntentional()) {
          $('#source').click();
        }
      }, function() {
        if (self.isIframeHoverIntentional()) {
          $('body').click();
        }
      });
    },


    /*
     * Removes all previously loaded entities and allows to load new ones
     */
    cleanupEntities: function() {
      this.entities = [];
      $('#entitylist .entity').remove();
      this.setNotOnPage();
    },


    /*
     * Update authors list in filter menu
     */
    updateAuthors: function (authors) {
      var self = this,
          $forAuthors = $('#filter').find('.for-authors').toggle(authors.length > 0);

      var selectedAuthors = $('#filter .menu li.author.selected').map(function() {
        return $.trim($(this).data("type"));
      }).get();

      $('#filter .menu li.author').remove();

      $.each(authors, function() {
        var selected = (selectedAuthors.includes(this.email)) ? ' selected' : '';
        $forAuthors.after('<li class="author' + selected + '" data-type="' + this.email + '">' +
          '<figure>' +
            '<span class="sel">' +
              '<span class="status fa"></span>' +
              '<img class="rounded" src="' + this.gravatar_url + '">' +
            '</span>' +
            '<figcaption>' +
              '<p class="name">' + this.display_name + '</p>' +
              '<p class="role">' + this.role + '</p>' +
            '</figcaption>' +
            '<span class="count">' + self.numberWithCommas(this.translation_count) + '</span>' +
          '</figure>' +
        '</li>');
      });
    },


    /*
     * Reset Time range filter to default
     */
    resetTimeRange: function() {
      $('#filter .time-range input').removeClass('error');

      if ($('#filter .horizontal-separator .edit').is('.editing')) {
        this.toggleRangeEditing();
      }
    },


    /*
     * Update save buttons based on user permissions and settings
     */
    updateSaveButtons: function () {
      $('[id^="save"]').toggleClass('suggest', !this.user.canTranslate() || this.user.forceSuggestions);
    },


    /*
     * Update textarea lang, dir and data-script attributes
     */
    updateTextareaAttributes: function () {
      $('#editor textarea')
        .attr('dir', this.locale.direction)
        .attr('lang', this.locale.code)
        .attr('data-script', this.locale.script);
    },


    /*
     * Update profile menu links and contents
     */
    updateProfileMenu: function () {
      var code = this.locale.code,
          slug = this.project.slug;

      $('#profile .admin-current-project a')
        .attr('href', '/admin/projects/' + slug + '/')
        .toggle(this.project.slug !== 'all-projects');
      $('#profile .upload').toggle(this.state.paths && this.user.canTranslate() && this.part !== 'all-resources');
      $('#profile .download, #profile .upload + .horizontal-separator').toggle(this.project.slug !== 'all-projects');

      $('#profile .langpack')
        .toggle(this.project.langpack_url !== '')
        .find('a').attr('href', this.project.langpack_url.replace('{locale_code}', this.locale.code));
      $('#profile .download-tmx a').attr('href', '/' + code + '/' + slug + '/' + code + '.' + slug + '.tmx');
    },


    /*
     * Show project info if available
     */
    updateProjectInfo: function () {
      var content = this.project.info;
      $('#info').hide().toggle(content !== "").find('.content').html(content);
    },


    /*
     * Mark current values and set links
     */
    updateMainMenu: function () {
      // Mark currect values
      $('header .menu li').removeClass('current');
      $('.project .menu li .name[data-slug=' + this.project.slug + '], ' +
        '.locale .menu li .language[data-code=' + this.locale.code + ']')
        .parent().addClass('current');
      $('.static-links .all-projects')
        .toggleClass('current', this.project.slug === 'all-projects');

      // Set current links
      $('.static-links .current-team')
        .parent().attr('href', '/' + this.locale.code);
      $('.static-links .current-project')
        .toggle(this.project.slug !== 'all-projects')
        .parent().attr('href', '/projects/' + this.project.slug);
      $('.static-links .current-localization')
        .parent().attr('href', '/' + this.locale.code + '/' + this.project.slug);

      this.updateGoButton();
    },


    /*
     * Reset entity list and editor width
     */
    resetColumnsWidth: function() {
      $('#entitylist, #editor').css('width', '');
    },


    /*
     * Show/hide elements needed for in place localization
     */
    toggleInplaceElements: function() {
      var inplaceElements = $('#source, #iframe-cover, #drag, #not-on-page').addClass('hidden').hide();

      if (this.project.win) {
        inplaceElements.removeClass('hidden').show();
      }
    },


    /*
     * Open first entity in the entity list in the editor
     */
    openFirstEntity: function() {
      $('#entitylist .entity:first').mouseover().click();
    },


    /*
     * Opens entity with the given id.
     */
    openEntity: function(entityId) {
      $('#entitylist .entity[data-entry-pk=' + entityId + ']').mouseover().click();
    },


    /*
     * Create user interface
     */
    createUI: function () {
      var self = this;

      // Show message if provided
      if ($('.notification li').length) {
        $('.notification').css('opacity', 100).removeClass('hide');
      }

      self.setMainLoading(false);
      self.toggleInplaceElements();
      self.resetColumnsWidth();
      self.updateMainMenu();
      self.updateProjectInfo();
      self.updateProfileMenu();
      self.updateTextareaAttributes();
      self.updateSaveButtons();
      self.resetTimeRange();
      self.updateFilterUI();
      self.renderEntityList();
      self.updateProgress();

      self.renderState();
    },


    /*
     * Render default UI
     */
    showDefaultView: function() {
      // If 2-column layout opened by default, open first entity in the editor
      if (this.app.advanced) {
        this.openFirstEntity();

      // If not and editor opened, show entity list
      } else if ($("#editor").is('.opened')) {
        this.goBackToEntityList();
      }
    },


    /*
     * Render UI based on application state
     */
    renderState: function() {
      var filter = this.state.filter,
          search = this.state.search,
          entity = this.state.entity;

      // No optional state parameters
      if (!filter.status && !filter.extra && !filter.time && !filter.author && !search && !entity) {
        this.showDefaultView();
        return;
      }

      if (entity) {
        if (!this.getEntityById(entity)) {
          this.endLoader("Can't load specified string.", 'error');
          this.showDefaultView();
          return;
        }
        this.openEntity(entity);

      } else {
        this.showDefaultView();

        if (this.requiresInplaceEditor()) {
          $('#entitylist .entity:not(.visible)').hide();
        }
      }

      if (this.requiresInplaceEditor()) {
        this.setNotOnPage();

        if (!this.hasVisibleEntities()) {
          this.setNoMatch(true);
        }
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
      if (Pontoon.project && !Pontoon.project.win) {
        return false;
      }
      otherWindow = otherWindow || Pontoon.project.win;
      targetOrigin = targetOrigin || Pontoon.project.url;
      var message = {
            type: messageType,
            value: messageValue
          };

      otherWindow.postMessage(JSON.stringify(message), targetOrigin);
    },


    /*
     * Get iframe width given the screen size and requested value
     */
    getProjectWidth: function () {
      var width = this.getProjectData('width') || false;
      if (($(window).width() - width) < 700) {
        width = false;
      }
      return width;
    },


    /*
     * Waits until Pontoon object attribute set.
     */
    waitForAttribute: function(propery, times, mainDeferred) {
      var self = this,
          d = mainDeferred || $.Deferred();
      // How many times should we check entities before displaying an error.
      times = typeof times === 'undefined' ? 100 : times;

      if (times === -1) {
        d.reject();
        return;
      }

      if (Pontoon[propery] && Pontoon[propery].length) {
        d.resolve();
      } else {
        setTimeout(function() {
          self.waitForAttribute(propery, times - 1, d);
        }, 100);
      }

      return d;
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
          clearInterval(Pontoon.interval);

          var advanced = false,
              websiteWidth = Pontoon.getProjectWidth();

          if (websiteWidth) {
            var windowWidth = $(window).width(),
                sidebarWidth = windowWidth - websiteWidth;

            if (sidebarWidth >= 700) {
              advanced = true;
              $('#sidebar').addClass('advanced').width(sidebarWidth);
              $('#editor').addClass('opened');

            } else {
              $('#sidebar').width(sidebarWidth);
              $('#editor').css('left', sidebarWidth);
            }
            Pontoon.setNotOnPage();

          } else {
            $('#sidebar').removeClass('advanced').css('width', '350px');
          }

          $('#source, #iframe-cover').css('margin-left', $('#sidebar').width() || 0);
          $('#source').show();

          Pontoon.ready = true;
          Pontoon.resizeIframe();
          Pontoon.makeIframeResizable();

          Pontoon.createObject(advanced, $('#source')[0].contentWindow);

          Pontoon.waitForAttribute('entities').then(function() {
            // Deep copy: http://api.jquery.com/jQuery.extend
            // Avoid circular structure, which is unable to convert to JSON
            var entities = $.extend(true, [], Pontoon.entities);
            $(entities).each(function () {
              delete this.ui;
            });

            Pontoon.postMessage("INITIALIZE", {
              path: Pontoon.app.path,
              links: Pontoon.project.links,
              entities: entities,
              slug: Pontoon.project.slug,
              locale: Pontoon.locale,
              user: Pontoon.user
            }, null, $('#source').attr('src'));
          }, $.proxy(Pontoon.noEntitiesError, Pontoon));
          break;

        case "DATA":
          // Deep copy: http://api.jquery.com/jQuery.extend
          Pontoon.waitForAttribute('entities').then(function() {
            Pontoon.entities = $.extend(
              true,
              Pontoon.entities,
              message.value.entities);
          });
          break;

        case "RENDER":
          var value = message.value;
          Pontoon.project.url = value.url;
          Pontoon.project.title = value.title;
          Pontoon.createUI();
          Pontoon.syncLocalStorageOnServer();
          break;

        case "HOVER":
          Pontoon.entities[message.value].ui.addClass('hovered');
          break;

        case "UNHOVER":
          Pontoon.entities[message.value].ui.removeClass('hovered');
          break;

        case "ACTIVE":
          var entity = Pontoon.entities[message.value];
          Pontoon.openEditor(entity);
          break;

        case "INACTIVE":
          if (!Pontoon.app.advanced && $("#editor").is('.opened')) {
            Pontoon.goBackToEntityList();
          }
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

        Pontoon.dragging = false;

        $('#iframe-cover').hide(); // iframe fix
        $('#sidebar:not(".batch") #editor:not(".opened")').css('left', $('#sidebar').width()).show();

        var initial = e.data.initial,
            advanced = Pontoon.app.advanced;
        if (initial.advanced !== advanced) {

          // On switch to 2-column layout, populate editor if empty
          if (advanced) {
            if (!$('#sidebar').is('.batch') && (!Pontoon.getEditorEntity() || !$('#entitylist .entity.hovered').length)) {
              Pontoon.openFirstEntity();
            }

          // On switch to 1-column layout, open editor if needed
          } else {
            if ($('#entitylist .entity.hovered').length) {
              Pontoon.openEditor(Pontoon.getEditorEntity());
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

        Pontoon.dragging = true;

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
        $('#sidebar:not(".batch") #editor:not(".opened")').hide();

        $(document)
          .bind('mousemove', { initial: data }, mouseMoveHandler)
          .bind('mouseup', { initial: data }, mouseUpHandler);
      });
    },


    /*
     * Create Pontoon object data
     *
     * advanced Is advanced (2-column) mode on?
     * projectWindow Website window object
     */
    createObject: function (advanced, projectWindow) {
      var self = this;

      this.app = {
        win: window,
        advanced: advanced,
        path: $('#server').data('site-url') + '/' // pontoon.css injection
      };

      this.part = this.getSelectedPart();

      this.locale = self.getLocaleData();

      // Convert CLDR plurals to Array
      if (!Array.isArray(this.locale.cldr_plurals)) {
        this.locale.cldr_plurals = this.locale.cldr_plurals.split(', ');
      }

      // Generate examples for CLDR plurals
      if (!this.locale.plural_examples) {
        self.generateLocalePluralExamples();
      }

      this.project = {
        win: projectWindow,
        url: "",
        title: "",
        slug: self.getProjectData('slug'),
        info: self.getProjectData('info') || '',
        width: self.getProjectWidth(),
        links: self.getProjectData('links') === 'True' ? true : false,
        langpack_url: self.getProjectData('langpack_url') || ''
      };

      /* Copy of User.can_translate(), used on client to improve performance */
      this.user.canTranslate = function() {
        var managedLocales = $('#server').data('user-managed-locales') || [],
            translatedLocales = $('#server').data('user-translated-locales') || [],
            translatedProjects = $('#server').data('user-translated-projects') || {},
            localeProject = self.locale.code + '-' + self.project.slug;

        if ($.inArray(self.locale.code, managedLocales) !== -1) {
          return true;
        }

        if (translatedProjects.hasOwnProperty(localeProject)) {
           return translatedProjects[localeProject];
        }

        return $.inArray(self.locale.code, translatedLocales) !== -1;
      };
    },


    /*
     * Load project with in place translation support
     */
    withInPlace: function() {
      var self = this,
          i = 0;

      self.interval = 0;

      // If no READY received for 10 seconds
      self.interval = setInterval(function() {
        i++;
        if (i > 100 && !self.ready) {
          clearInterval(self.interval);
          window.removeEventListener("message", self.receiveMessage, false);
          return self.withoutInPlace();
        }
      }, 100);

      // In case READY sent before we could catch it
      self.postMessage(
        "ARE YOU READY?",
        null,
        $('#source').prop('contentWindow'),
        $('#source').attr('src')
      );
    },


    /*
     * Load project without in place translation support
     */
    withoutInPlace: function() {
      var self = this;
      $('#sidebar').addClass('advanced').css('width', '100%');
      $('#entitylist').css('left', '');

      self.createObject(true);

      $(self.entities).each(function (i) {
        this.id = i;
      });

      self.createUI();

      if (self.hasVisibleEntities()) {
        $('#editor').addClass('opened').css('left', '');
      } else {
        self.setNoMatch(true);
      }

      self.syncLocalStorageOnServer();
    },


    /*
     * Manipulates the loading overlay
     */
    setMainLoading: function(enabled) {
      clearTimeout(this.mainLoadingTimer);
      $('#project-load').toggle(enabled).find('.text').css('opacity', 0);

      // Show potentially amusing message if loading takes more time
      if (enabled) {
        this.mainLoadingTimer = setTimeout(function() {
          $('#project-load .text').animate({opacity: 1});
        }, 3000);
      }
    },


    /*
     * Tells if current project requires Inplace Editor
     */
    requiresInplaceEditor: function() {
      var part = this.currentPart;
      return part && part.url;
    },


    /*
     * Get paths for the selected part
     */
    getPartPaths: function(part) {
      var paths = part.resource__path;
      if (paths.constructor === Array) {
        return paths;
      }

      return [paths];
    },


    /*
     * Load entities, store data, prepare UI
     */
    getEntities: function(opts) {
      opts = opts || {};
      var self = this,
          state = self.state,
          params = {
            'project': state.project,
            'locale': state.locale,
            'paths': self.getPartPaths(self.currentPart),
            'search': self.getSearch(),
            'status': self.getFilter('status').join(','),
            'extra': self.getFilter('extra').join(','),
            'time': self.getFilter('time'),
            'author': self.getFilter('author').join(','),
            'inplace_editor': self.requiresInplaceEditor()
          },
          deferred = $.Deferred();

      if (self.XHRgetEntities) {
        self.XHRgetEntities.abort();
      }

      $.extend(params, opts);

      self.XHRgetEntities = $.ajax({
        type: 'POST',
        url: '/get-entities/',
        data: params,
        success: function(data) {
          deferred.resolve(data, data.has_next);
        },
        error: function(data, text) {
          deferred.reject(text);
        }
      });

      return deferred;
    },


    /*
     * Process entities if returned, considering in place support
     */
    processEntities: function(entitiesData, hasNext) {
      var self = this;

      self.stats = entitiesData.stats;
      self.entities = entitiesData.entities;
      self.hasNext = hasNext;

      self.updateTitle();

      // No entities found
      if (!self.entities.length) {
        if (!self.requiresInplaceEditor()) {
          $('#sidebar').addClass('advanced').css('width', '100%');
          $('#iframe-cover').addClass('hidden').hide();
          self.setNotOnPage();
          self.setNoMatch(true);
          self.setMainLoading(false);
          self.updateProgress();
          self.updateFilterUI();
          self.createObject(true);
          return;
        }
      } else {
        self.setNoMatch(false);
      }

      if (self.requiresInplaceEditor()) {
        if (!self.ready) {
          self.withInPlace();
        }
      } else {
        self.withoutInPlace();
      }
    },


    /*
     * Displays an error if unable to get entities
     */
    noEntitiesError: function() {
      // Do not show an error if other request in progress
      if (this.XHRgetEntities && this.XHRgetEntities.statusText === 'abort') {
        return;
      }

      $('#project-load')
        .find('.animation').hide().end()
        .find('.text')
          .html('Oops, something went wrong.')
          .animate({opacity: 1});
    },


    /*
     * Request entities and website for selected part
     */
    initializePart: function(forceReloadIframe) {
      var self = this,
          entitiesOpts = {};

      self.cleanupEntities();
      this.clearSelection();

      self.ready = null;
      self.setMainLoading(true);

      if (self.state.entity) {
        entitiesOpts.entity = self.state.entity;
      }

      self.getEntities(entitiesOpts)
          .then($.proxy(self.processEntities, self), $.proxy(self.noEntitiesError, self));

      if (self.requiresInplaceEditor()) {
        var url = self.currentPart.url;

        if ($('#source').attr('src') !== url || forceReloadIframe) {
          $('#source').attr('src', url);
        }
        window.addEventListener("message", self.receiveMessage, false);
      }
    },


    setSidebarLoading: function(state) {
      $('#entitylist .loading').toggle(state);
      if (state) {
        $('#entitylist .no-match').hide();
      }
    },


    setNoMatch: function(noMatch) {
      $('#entitylist .no-match').toggle(noMatch);
      $('#sidebar').toggleClass('no', noMatch);
    },


    isLoading: function() {
      return $('#entitylist .loading').css('display') === 'block';
    },


    hasVisibleEntities: function() {
      return $('#entitylist li:visible').length > 0;
    },


    getEntitiesIds: function(selector) {
      return $.map($(selector || '#entitylist .entity:visible'), function(item) {
        return $(item).data('entry-pk');
      });
    },


    /*
     * Returns an entity object with given id
     */
    getEntityById: function(entityId, entities) {
      entities = entities || this.entities;

      return entities.find(function(entity) {
        return entity.pk === parseInt(entityId);
      });
    },


    /*
     * Returns currently opened entity object
     */
    getEditorEntity: function() {
      var $editor = $('#editor'),
          $sidebar = $('#sidebar');

      if ((this.requiresInplaceEditor() && !$editor.is('.opened') && this.project.url) ||
          (!this.requiresInplaceEditor() && $sidebar.is('.no'))) {
        return;
      }
      return $editor[0].entity;
    },


    getEditorEntityPk: function() {
      var entity = this.getEditorEntity();

      if (entity) {
        return entity.pk;
      }
    },


    isEditorEntityAvailable: function() {
      var availableEntityIds = this.getEntitiesIds();

      return availableEntityIds.indexOf(this.getEditorEntityPk()) > -1;
    },

    highlightQuery: function(item) {
      var searchQuery = this.getSearch();
      item = item || $('#entitylist .source-string, #entitylist .translation-string');

      item.unmark();
      if (searchQuery) {
        searchQuery = ((searchQuery.split('"').length-1)%2)? searchQuery+'"':searchQuery;
        var queries = searchQuery.match(/\w+|"[^"]+"/g);
        if (!queries) return;
        var i = queries.length;
        while(i--){
          queries[i] = queries[i].replace(/"/g,"");
        }
        // sort array in decreasing order of string length
        queries.sort(function(a,b) {
          return b.length - a.length;
        });
        queries.forEach(function(query) {
          item.mark(query, {
          acrossElements: true,
          caseSensitive: false,
          className: 'search',
          separateWordSearch: false
          });
        });
      }
    },

    loadNextEntities: function(type) {
      var self = this,
          requiresInplaceEditor = self.requiresInplaceEditor(),
          // Join IDs into string due to bug 1344322
          excludeEntities = requiresInplaceEditor ? {} : {exclude_entities: self.getEntitiesIds('#entitylist .entity').join(',')};

      self.setSidebarLoading(true);

      self.getEntities(excludeEntities).then(function(entitiesData, hasNext) {
        self.entities = self.entities.concat(entitiesData.entities);
        self.hasNext = hasNext;

        if (requiresInplaceEditor) {
          $(entitiesData.entities).each(function (idx, entity) {
            if (entity.visible) {
              self.showEntity(entity);
            }
          });
          self.setNotOnPage();

        } else {
          $(entitiesData.entities).map($.proxy(self.renderEntity, self)).each(function (idx, entity) {
            self.appendEntity(entity);
          });
        }

        if(!hasNext && !self.hasVisibleEntities()) {
          self.setNoMatch(true);
        } else {
          self.setNoMatch(false);
          self.highlightQuery();

          if (self.app.advanced && type !== 'scroll') {
            if (self.isEditorEntityAvailable()) {
              var ui = $('#entitylist .entity[data-entry-pk=' + self.getEditorEntityPk() + ']');
              ui.addClass('hovered');
              self.getEditorEntity().ui = ui; // DOM node might have been replaced
            } else {
              self.openFirstEntity();
            }
            $('#search').focus();
          }
        }
        self.pushState();
      }).always(function() {
        // Skip if other request in progress
        if (self.XHRgetEntities && self.XHRgetEntities.statusText === 'abort') {
          return;
        }
        self.setSidebarLoading(false);
      });
    },


    /*
     * Get currently selected locale code
     */
    getSelectedLocale: function() {
      return $('.locale .selector .language').data('code');
    },


    /*
     * Get currently selected project slug
     */
    getSelectedProject: function() {
      return $('.project .button .title').data('slug');
    },


    /*
     * Get currently selected part name
     */
    getSelectedPart: function() {
      var part = $('.part .selector').attr('title');
      if (part === 'All Resources') {
        part = 'all-resources';
      }
      return part;
    },


    /*
     * Get data-* attribute value of the currently selected locale
     */
    getLocaleData: function(attribute) {
      var code = this.getSelectedLocale();
      return $('.locale .menu li .language[data-code=' + code + ']').data(attribute);
    },


    /*
     * Get data-* attribute value of the currently selected project
     */
    getProjectData: function(attribute) {
      var slug = this.getSelectedProject();
      return $('.project .menu .name[data-slug=' + slug + ']').data(attribute);
    },


    /*
     * Update currently selected part object
     *
     * title Part title
     */
    updateCurrentPart: function() {
      var locale = this.getSelectedLocale(),
          part = this.getSelectedPart(),
          availableParts = this.getProjectData('parts')[locale],
          matchingParts = $.grep(availableParts, function (e) {
            return e.title === part;
          });

      if (!matchingParts.length) {
        this.currentPart = availableParts[0];
      } else {
        this.currentPart = matchingParts[0];
      }

      this.updatePartSelector(this.currentPart.title);
    },


    /*
     * Update title of the current view.
     */
    updateTitle: function() {
      var project = this.getProjectData(),
          locale = this.getLocaleData();

      document.title = project.name + ' · ' + locale.name + ' (' + locale.code + ')';
    },


    /*
     * Updates Pontoon and history state, and the URL
     */
    pushState: function(state) {
      state = state || this.getState();
      var self = this,
          url = '/' + state.locale + '/' + state.project + '/' + state.paths + '/',
          queryParams = {};

      self.state = state;

      // Keep homepage URL
      if (window.location.pathname === '/' && state.project === 'pontoon-intro') {
        url = '/';
      }

      if (state.filter.status.length > 0) {
        queryParams.status = state.filter.status.join(',');
      }

      if (state.filter.extra.length > 0) {
        queryParams.extra = state.filter.extra.join(',');
      }

      if (state.filter.time) {
        queryParams.time = state.filter.time;
      }

      if (state.filter.author.length > 0) {
        queryParams.author = state.filter.author.join(',');
      }

      if (state.search && state.search !== '') {
        queryParams.search = state.search;
      }

      if (state.entity) {
        queryParams.string = state.entity;
      }

      if (!$.isEmptyObject(queryParams)) {
        url += '?' + $.param(queryParams);
      }

      if (JSON.stringify(history.state) !== JSON.stringify(self.state)) {
        history.pushState(state, '', url);
      }
    },


    /*
     * Get value from the querystring
     */
    getQueryParam: function(name) {
      name = name.replace(/[[\]]/g, "\\$&");
      var url = window.location.href,
          regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)", "i"),
          results = regex.exec(url);

      if (!results || !results[2]) {
        return null;
      }

      var encodedURI = results[2].replace(/\+/g, " ");

      try {
        return decodeURIComponent(encodedURI);

      // If querystring not encoded, we need to encode it first
      } catch (e) {
        if (e instanceof URIError) {
          encodedURI = encodeURIComponent(encodedURI);
          return decodeURIComponent(encodedURI);
        }
      }
    },


    /*
     * Get current application state
     *
     * type If 'selected', get selected main menu state (instead of currently translated)
     */
    getState: function(type) {
      return {
        project: type === 'selected' ? this.getSelectedProject() : this.project.slug,
        locale: type === 'selected' ? this.getSelectedLocale() : this.locale.code,
        paths: type === 'selected' ? this.getSelectedPart() : this.part,
        filter: this.getFilter(),
        search: this.getSearch(),
        entity: this.getEditorEntityPk()
      };
    },


    /*
     * Update initial Pontoon state from the URL
     */
    updateInitialState: function() {
      var state = this.getState('selected');
      state.filter = {
        status: this.getQueryParam('status') ? this.getQueryParam('status').split(',') : [],
        extra: this.getQueryParam('extra') ? this.getQueryParam('extra').split(',') : [],
        time: this.getQueryParam('time'),
        author: this.getQueryParam('author') ? this.getQueryParam('author').split(',') : []
      };
      state.search = this.getQueryParam('search');
      state.entity = this.getQueryParam('string');

      // Update search and filter
      this.setSearch(state.search);
      this.validateTimeRangeURL(state.filter);
      this.updateFilterUI(state.filter);

      // Fallback to first available part if no matches found (mistyped URL)
      var requestedPaths = this.getSelectedPart(),
          paths = requestedPaths;
      this.updateCurrentPart(requestedPaths);
      paths = this.currentPart.title;

      if (paths !== requestedPaths) {
        state.paths = paths;
        this.pushState(state);
      } else {
        this.state = state;
      }
    }
  });
}(Pontoon || {}));

/* Main code */
window.onpopstate = function(e) {
  if (e.state) {
    // Update main menu
    $('.project .menu .name[data-slug="' + e.state.project + '"]').parent().click();
    $('.locale .menu li .language[data-code="' + e.state.locale + '"]').parent().click();

    if (e.state.paths) {
      // Also update part, otherwise the first one gets selected
      Pontoon.updateCurrentPart(e.state.paths);
    }

    Pontoon.state = history.state;

    // Update search and filter
    Pontoon.setSearch(Pontoon.state.search);
    Pontoon.validateTimeRangeURL(Pontoon.state.filter);
    Pontoon.updateFilterUI(Pontoon.state.filter);

    Pontoon.initializePart(true);
  }
};

Pontoon.user = {
  id: $('#server').data('id') || '',
  display_name: $('#server').data('display-name'),
  forceSuggestions: $('#server').data('force-suggestions') === 'True' ? true : false,
  manager: $('#server').data('manager'),
  localesOrder: $('#server').data('locales-order') || {},
};

Pontoon.attachMainHandlers();
Pontoon.attachEntityListHandlers();
Pontoon.attachEditorHandlers();
Pontoon.attachBatchEditorHandlers();

Pontoon.updateInitialState();
Pontoon.updateFilterUI();
Pontoon.initializePart();
