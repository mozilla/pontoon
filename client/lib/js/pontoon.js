var Pontoon = (function () {

  'use strict';

  /* public  */
  return {



    /*
     * Save data to server
     * Pontoon server push expects a POST with the following properties:
     *
     * id - list of msgid strings, the length of id should match the length of value ['Hello World']
     * value - list of msgstrs, should be empty if no changes, otherwise set to the edited value ['Hallo Welt']
     * project - url of the page being localized
     * locale - locale msgstrs are localized too
    */
    save: function () {
      var url = this.client._meta.url || 'http://0.0.0.0:8000/push/',
          project = this.client._meta.project || this.client._doc.location.href,
          params = {
            'project': project,
            'locale': this.client._locale
          },
          // Deep copy: http://api.jquery.com/jQuery.extend
          data = $.extend(true, {}, this.client._data);

      $(data.entities).each(function () {
        delete this.node;
        delete this.ui;
        delete this.hover;
        delete this.unhover;
      });

      // TODO: add, support other browsers - https://developer.mozilla.org/en/Using_JSON_in_Firefox
      params.data = JSON.stringify(data);
      
      $.ajaxSettings.traditional = true;
      $.post(url, params);
    },



    /*
     * Do not render HTML code
     *
     * string HTML snippet that has to be displayed as code instead of rendered
    */
    doNotRender: function (string) {
      return string.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },



    /**
     * Build source - translation pairs
     */
    entityList: function () {
      var self = this,
          list = $(this.client._ptn).find('#entitylist').empty().append('<ul></ul>');

      // Render
      $(this.client._data.entities).each(function () {
        var li = $('<li class="entity' + 
          // append classes to translated and head entities
          (this.translation ? ' translated' : '') + 
          (!this.node ? ' head' : '') + '">' + 
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
              '<header class="select">' + 
                '<h3 class="selector">' + 
                  '<span class="flag"></span>' + 
                  '<span class="language">Select locale</span>' + 
                  '<span class="handle"> &#9662;</span>' + 
                '</h3>' + 
                '<ul class="menu">' + 
                  '<li><span class="flag de"></span><span class="language">Deutsch</span></li>' + 
                  '<li><span class="flag fr"></span><span class="language">Français</span></li>' + 
                  '<li><span class="flag hr"></span><span class="language">Hrvatski</span></li>' + 
                  '<li><span class="flag pl"></span><span class="language">Polski</span></li>' + 
                  '<li><span class="flag sl"></span><span class="language">Slovenščina</span></li>' + 
                '</ul>' + 
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
              '<a href="#cancel" class="cancel" title="Cancel and revert to initial translation"></a>' + 
            '</div>' +
          '</div>' +
        '</div></li>', self.client._ptn);

        li.get(0).entity = this;
        if (this.node) { // For entities found on the website
          this.node.get(0).entity = this;
        }
        this.ui = li; /* HTML Element representing string in the main UI */

        list.children('ul').append(li);
      });

      // Main entity list handlers
      $("#main .entity:not('.head')").hover(function () {
        this.entity.hover();
      }, function () {
        this.entity.unhover();
      }).click(function () {
        $(self.client._doc).find('.editableToolbar > .edit').click();
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
        if ($(this).siblings(".menu").is(":visible")) {
          $("#main .source .other-locales .menu").hide();
        } else {
          $("#main .source .other-locales .menu").hide();
          $(this).siblings('.menu').show();
        }
      });
      $("#main .source .other-locales .select .menu li").click(function (e) {
        e.stopPropagation();
        var li = $(this),
            entity = li.parents(".entity"),
            index = entity.index(), /* TODO: use IDs or XPath */
            locale = li.find(".flag").attr("class").split(" ")[1],
            p = li.parents('.select').next('p').show();

        li.parents('.menu').siblings('.selector')
          .find('.flag').attr("class", li.find('.flag').attr('class')).show().end()
          .find('.language').html(li.find('.language').html()).end().end()
        .hide();

        // TODO: AJAX request to display only locales with current string translation available
        if (locale === "sl") {
          // TODO: Only request each locale meta file once
          $.getJSON($("#source").attr("src") + "/pontoon/" + locale + ".json").success(function (data) {
            var translation = data.entities[index].translation;
            if (translation) {
              p.removeClass("no").addClass("source-string").html(translation);
              entity.find('.toolbar').show();
            } else {
              p.addClass("no").html('No translations yet');
              entity.find('.toolbar').hide();
            }
          });
        } else {
          p.addClass("no").html('No translations yet');
          entity.find('.toolbar').hide();
        }
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
              locale: self.client._locale,
              whole_word: 'whole_word',
              repo: 'beta'
            },
            dataType: 'jsonp'
          }).error(function () {
            loader.removeClass("loader").addClass("no").html("Ooops, something went wrong... Please try again.");
          }).success(function (response) {
            if (response !== null) {
              // Not supported in some browsers, but needed with current JSON output:
              // https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Object/keys
              // TODO - use this kind of output: http://pastebin.mozilla.org/1316020
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
            entity = li.get(0).entity;
        if (loader.length === 0) {
          li.find(".toolbar").show();
        } else {
          $.translate(entity.original, self.client._locale, {
            complete: function (t) {
              loader.removeClass("loader").addClass("source-string").html(self.doNotRender(t));
              li.find(".toolbar").show();
            }
          });
        }
      });

      // Copy source to translation
      $("#main .source .copy").click(function (e) {
        e.stopPropagation();
        var toolbar = $(self.client._doc).find('.editableToolbar'),
            li = $(this).parents('.entity'),
            entity = li.get(0).entity,
            source = li.find('.source .content .active .source-string').html();

        // Only if no other entity is being edited in-place
        if (entity.node && entity.node.is('.hovered')) {
          $(entity.node).html(source);
          toolbar.find('.save').click();
        // Head entities cannot be edited in-place
        } else if (!entity.node) {
          entity.translation = source;
          self.updateEntityUI(entity);
        }
      });

      // Translate in textarea
      $("#main .translation textarea").click(function (e) {
        e.stopPropagation();
        var entity = $(this).parents('.entity').get(0).entity;

        // Only if no other entity is being edited in-place
        if (entity.node && !entity.node.is('.hovered')) {
          $(this).blur();
        }
      });

      $("#main .translation .save").click(function (e) {
        e.stopPropagation();
        var toolbar = $(self.client._doc).find('.editableToolbar'),
            li = $(this).parents('.entity'),
            entity = li.get(0).entity,
            source = li.find('.translation textarea').val();

        // Only if no other entity is being edited in-place
        if (entity.node && entity.node.is('.hovered')) {
          $(entity.node).html(source);
          toolbar.find('.save').click();
        // Head entities cannot be edited in-place
        } else if (!entity.node) {
          entity.translation = source;
          self.updateEntityUI(entity);
        }
      });

      $("#main .translation .cancel").click(function (e) {
        e.stopPropagation();
        var toolbar = $(self.client._doc).find('.editableToolbar'),
            li = $(this).parents('.entity'),
            entity = li.get(0).entity;

        // Only if no other entity is being edited in-place
        if (entity.node && entity.node.is('.hovered')) {
          toolbar.find('.cancel').click();
        // Head entities cannot be edited in-place
        } else if (!entity.node) {
          entity.translation = "";
          entity.ui.find('textarea').val(entity.translation).parents('.entity').removeClass('translated');
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
     * Attach event handlers
     */
    attachHandlers: function () {
      var self = this;

      // Update entities and progress when saved
      $(".editableToolbar > .save", this.client._doc).click(function () {
        var element = $(this).parent().get(0).target,
            entity = element.entity;

        entity.translation = $($(element).clone()).html();
        self.updateEntityUI(entity);
      });

      // Update progress when cancelled
      $(".editableToolbar > .cancel", this.client._doc).click(function () {
        var element = $(this).parent().get(0).target,
            entity = element.entity;

        $(element).html(element.prevValue);
        entity.translation = "";
        entity.ui.find('textarea').val(entity.translation).parents('.entity').removeClass('translated');
        self.updateProgress();
      });

      // Open/close Pontoon UI
      $('#switch').unbind("click.pontoon").bind("click.pontoon", function () {
        if ($('#main').is('.opened')) {
          $('#entitylist').height(0);
        } else {
          $('#entitylist').height(300);
        }
        $('#source').height($(document).height() - $('#main').height());
        $('#main').toggleClass('opened');
      });

      // Authentication
      $('#authentication-menu .restricted .go').unbind("click.pontoon").bind("click.pontoon", function () {
        var author = $('#nickname').val() || $('#email').val();
        $('#authentication .selector').click();
        if (author) {
          $('#authentication .author').html(author).toggleClass('authenticated');
          $('#authentication-menu, #save-menu').toggleClass('menu');
        }
      });
      $('#nickname').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        var key = e.keyCode || e.which;
        if (key === 13) { // Enter
          $('#authentication-menu .restricted .go').click();
          return false;
        }
      });

      // Authentication toggle
      $('#authentication-menu .toggle').unbind("click.pontoon").bind("click.pontoon", function () {
        $('#authentication-menu')
          .find('.wrapper').toggle().end()
          .find('#password').toggle();
      });

      // Save menu
      $('#save-menu').find('.sign-out').unbind("click.pontoon").bind("click.pontoon", function () {
        $('#authentication .selector').click();
        $('#authentication .author').html('Sign in').toggleClass('authenticated');
        $('#authentication-menu, #save-menu').toggleClass('menu');
      }).end().find('.server').unbind("click.pontoon").bind("click.pontoon", function () {
        $('#authentication .selector').click();
        self.save();
      });

      // In-place keyboard shortcuts
      $("html", self.client._doc).unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        var key = e.keyCode || e.which,
            toolbar = $(".editableToolbar", self.client._doc),
            save = toolbar.find(".save"),
            ui = toolbar.get(0).target.entity.ui,
            next = ui.next();

        if (save.is(":visible")) {
          if (key === 13) { // Enter: confirm translation
            save.click();
            toolbar.get(0).target.hideToolbar();
            return false;
          }

          if (key === 27) { // Esc: cancel translation
            toolbar.find(".cancel").click();
            toolbar.get(0).target.hideToolbar();
            return false;
          }

          if (key === 9) { // Tab: confirm + move around entities
            // If on last entity, jump to the first
            if (next.length === 0) {
              next = $(".entity:not('.head'):first");
            }

            save.click();
            $(toolbar.get(0).target).removeClass("hovered");
            next.get(0).entity.hover();
            next.click();
            return false;
          }
        }
      });

    },



    /**
     * Show and render main UI
     * Enable editable text
     */
    renderMainUI: function () {
      $(this.client._data.entities).each(function () {
        if (this.node) { // For entities not found on the website
          this.node.editableText();
        }
      });
      this.attachHandlers();
      this.entityList();
      $('#main').slideDown();
    },



    /**
     * Update entity in the main UI
     * 
     * entity Entity
     */
    updateEntityUI: function (entity) {
      entity.ui.find('textarea').val(entity.translation).parents('.entity').addClass('translated');
      this.updateProgress();
    },



    /**
     * Extend entity object
     * 
     * e Temporary entity object
     */
    extendEntity: function (e) {
      e.hover = function () {
        this.node.get(0).showToolbar();
        this.ui.toggleClass('hovered');
      };
      e.unhover = function () {
        this.node.get(0).hideToolbar();
        this.ui.toggleClass('hovered');
      };
    },



    /**
     * Extract entities from the document, not prepared for working with Pontoon
     * 
     * Create entity object from every non-empty text node
     * Exclude nodes from special tags, e.g. <script> and <link>
     * Skip nodes already included in parent nodes
     * Add temporary pontoon-entity class to prevent duplicate entities when guessing
     */ 
    guessEntities: function () {
      var self = this;
      this.client._data.entities = [];

      $(this.client._doc).find(':not("script, style")').contents().each(function () {
        if (this.nodeType === Node.TEXT_NODE && $.trim(this.nodeValue).length > 0 && $(this).parents(".pontoon-entity").length === 0) {
          var entity = {};
          entity.original = $(this).parent().html();

          // Head entities cannot be edited in-place
          if ($(this).parents('head').length === 0) {
            entity.node = $(this).parent(); /* HTML Element holding string */
            self.extendEntity(entity);
          }

          self.client._data.entities.push(entity);
          $(this).parent().addClass("pontoon-entity");
        }
      });

      $(this.client._doc).find(".pontoon-entity").removeClass("pontoon-entity");
      self.renderMainUI();
    },



    /**
     * Get data from external meta file: original string, translation, comment, suggestions...
     * Match with each string in the document, which is prepended with l10n comment nodes
     * Example: <!--l10n-->Hello World
     *
     * Create entity objects
     * Remove comment nodes
     */
    getEntities: function () {
      var self = this,
          prefix = 'l10n',
          counter = 1, /* TODO: use IDs or XPath */
          parent = null;

      $.getJSON($("#source").attr("src") + "/pontoon/" + this.client._locale + ".json").success(function (data) {
        self.client._data = data;
        var entities = self.client._data.entities;

        $(self.client._doc).find('*').contents().each(function () {
          if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf(prefix) === 0) {
            var entity = entities[counter],
                translation = entity.translation;

            parent = $(this).parent();
            if (translation.length > 0) {
              parent.html(translation);
            } else {
              $(this).remove();
            }

            entity.node = parent; /* HTML Element holding string */
            self.extendEntity(entity);
            counter = counter + 1;
          }
        });
        self.renderMainUI();
      });
    },



    /**
     * Extract entities from the document
     * Determine if the current page is prepared for working with Pontoon
     */ 
    extractEntities: function () {
      var meta = $(this.client._doc).find('head > meta[name=Pontoon]');
      if (meta.length > 0) {
        if (meta.attr('content')) {
          this.client._meta.project = meta.attr('content');
        }
        if (meta.attr('ip')) {
          this.client._meta.url = meta.attr('ip');
        }
        return this.getEntities();
      }

      // Read meta values
      return this.guessEntities();
    },



    /**
     * Initialize Pontoon Client
     *
     * doc Website document object
     * ptn Pontoon document object
     * locale ISO 639-1 language code of the language website is localized to
     */
    init: function (doc, ptn, locale) {
      if (!doc) {
        throw "Document handler required";
      }

      var self = this,
          ss = $('<link rel="stylesheet" href="../../client/lib/css/editable.css">', doc);

      // Build client object
      this.client = {
        _doc: doc,
        _ptn: ptn,
        _locale: locale,
        _meta: {},
        _data: {},
        _mt: ''
      };

      // Enable document editing
      $('head', doc).append(ss);      
      this.extractEntities();       

      // Context menu
      $('body', doc)
        .attr("contextmenu", "context")
        .append(
        '<menu type="context" id="context">' +
          '<menuitem label="Advanced mode" icon="../../client/lib/images/logo-small.png"></menuitem>' +
        '</menu>')
        .find("#context menuitem").live("click", function() {
          $("#switch").click();
          if ($("#main").is(".opened")) {
            $(this).attr("label", "Basic mode");
          } else {
            $(this).attr("label", "Advanced mode");
          }
        });

      // Instantate Microsoft Translator API
      $.getScript("client/lib/js/local-settings.js", function () {
        $.translate.load(self.client._mt);
      });
    },



    /**
     * Common functions used in both, client specific code and Pontoon library
     */
    common: function () {

      // Show/hide menu on click
      $('.selector').unbind("click.pontoon").bind("click.pontoon", function (e) {
        if (!$(this).siblings('.menu').is(':visible')) {
          e.stopPropagation();
          $('.menu').hide();
          $('#iframe-cover').hide(); // iframe fix
          $('.select').removeClass('opened');
          $(this).siblings('.menu').show();
          $('#iframe-cover').show().height($('#source').height()); // iframe fix
          $(this).parents('.select').addClass('opened');
        }
      });

      // Hide menus on click outside
      $('html').unbind("click.pontoon").bind("click.pontoon", function () {
        $('.menu').hide();
        $('#iframe-cover').hide(); // iframe fix
        $('.select').removeClass('opened');
      });
      $('.menu').unbind("click.pontoon").bind("click.pontoon", function (e) {
        e.stopPropagation();
      });

      // Start new project with current website url and locale
      $('.locale .confirm, .locale .menu li:not(".add")').unbind("click.pontoon").bind("click.pontoon", function () {
        // TODO: url and locale validation
        window.location = "?url=" + $('.url:visible').val() + "&locale=" + $(this).find('.flag').attr('class').split(' ')[1];
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

      // Use arrow keys to move around menu, confirm with enter, close with escape
      $('html').unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
        if ($('.menu').is(':visible')) {
          var key = e.keyCode || e.which,
              menu = $('.menu:visible'),
              hovered = menu.find('li.hover');

          if (key === 38) { // up arrow
            if (hovered.length === 0 || menu.find('li:first').is('.hover')) {
              menu.find('li.hover').removeClass('hover');
              menu.find('li:last').addClass('hover');
            } else {
              menu.find('li.hover').removeClass('hover').prev().addClass('hover');
            }
            return false;
          }

          if (key === 40) { // down arrow
            if (hovered.length === 0 || menu.find('li:last').is('.hover')) {
              menu.find('li.hover').removeClass('hover');
              menu.find('li:first').addClass('hover');
            } else {
              menu.find('li.hover').removeClass('hover').next().addClass('hover');
            }
            return false;
          }

          if (key === 13) { // Enter
            menu.find('li.hover').click();
            return false;
          }

          if (key === 27) { // Escape
            menu.siblings('.selector').click();
            return false;
          }
        }
      });
    }

  };
}());
