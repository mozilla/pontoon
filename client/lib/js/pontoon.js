var Pontoon = function() {

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
    save: function() {
      // Deep copy: http://api.jquery.com/jQuery.extend
      var data = jQuery.extend(true, {}, this.client._data);

      $(data.entities).each(function() {
        delete this.node;
        delete this.ui;
        delete this.hover;
        delete this.unhover;
      });

      var self = this,
          url = ('url' in this.client._meta) ? this.client._meta['url'] : 'http://127.0.0.1:8000/push/',
          project = ('project' in this.client._meta) ? this.client._meta['project'] : this.client._doc.location.href,
          locale = $(this.client._ptn).find('input').val(),
          params = {
            'project': project,
            'locale': locale,
            // TODO: add, support other browsers - https://developer.mozilla.org/en/Using_JSON_in_Firefox
            'data': JSON.stringify(data)
          };

      $.ajaxSettings.traditional = true;
      $.post(url, params);
    },
  
  
  
    /*
     * Set language using browser language detection
     *
     * Browser language cannot be generally obtained via navigator.language
     * Using HTTP 'Accept-Language' header via external service temporary
     * Source: http://stackoverflow.com/questions/1043339/javascript-for-detecting-browser-language-preference
     *
     * TODO: explore Jetpack options and develop internal solution
    */
    setLanguage: function() {
      /*
      $.ajax({ 
        url: "http://ajaxhttpheaders.appspot.com", 
        dataType: 'jsonp', 
        success: function(headers) {
          var language = headers['Accept-Language'].substring(0, 2),
              entry = $('#locale-menu .flag.' + language);
          if (entry.length !== 0) {
            $('#flag').addClass(language);
            $('#locale .selector .language').html(entry.next().text());
          }
        }
      }).done(function() {
        $('#pontoon').slideDown();
      });
      */
      $('#pontoon').slideDown();
    },



    /*
     * Do not render HTML code
     *
     * string : explore Jetpack options and develop internal solution
    */
    doNotRender: function(string) {
      return string.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },



    /**
     * Build source - translation pairs
     */
    rebuildList: function() {
      var self = this,
          list = $(this.client._ptn).find('#entitylist').empty()
          // tables still need 'cellspacing="0"' in the markup
          // http://meyerweb.com/eric/thoughts/2007/05/01/reset-reloaded/
          .append(
            '<table cellpadding="0" cellspacing="0" border="0">' + 
              '<thead><tr><th>Source</th><th>Translation</th></tr></thead>' + 
              '<tbody></tbody>' + 
            '</table>');
  
      // Render
      $(this.client._data.entities).each(function() {
        var tr = $('<tr' + (this.translation ? ' class="translated"' : '') + '>' + 
        '<td class="source">' + 
          '<p>' + self.doNotRender(this.original) + '</p>' + 
          '<ul class="tools">' + 
            '<li title="Copy original string to translation" class="copy"></li>' + 
            '<li title="Machine translation by Google Translate" class="auto-translate"></li>' + 
            (this.comment ? '<li title="' + this.comment + '" class="comment"></li>' : '') + 
          '</ul>' + 
        '</td>' +
        '<td class="translation">' + 
          '<div class="suggestions">' + 
            '<a href="#translation" class="translation active">Translation</a>' + 
            '<a href="#translation-memory" class="tm">Translation memory</a>' + 
            '<a href="#other-users" class="users">Other users</a>' + 
            '<a href="#other-locales" class="locales">Other locales</a>' + 
          '</div>' + 
          '<textarea>' + (this.translation || '') + '</textarea>' + 
        '</td></tr>', self.client._ptn);
            
        tr.get(0).entity = this;
        if (this.node) { // For entities not found on the website
          this.node.get(0).entity = this;
        }
        this.ui = tr;
  
        list.find('tbody').append(tr);
      });
  
      // Main entity list handlers
      $("#pontoon tr").hover(function() {
        this.entity.hover();
      }, function() {
        this.entity.unhover();
      }).click(function() {
        $(self.client._doc).find('.editableToolbar > .edit').click();
      });
  
      // Copy original string to translation
      $("#pontoon .copy").click(function(e) {
      	e.stopPropagation();
        var toolbar = $(self.client._doc).find('.editableToolbar');
        toolbar.find('.edit').click().end();

      	var entity = $(this).parents('tr').get(0).entity;
      	$(entity.node).html(entity.original);
        toolbar.find('.save').click();
      });
  
      this.updateProgress();
    },
  
  
  
    /**
     * Update progress indicator and value
     */
    updateProgress: function() {
      var all = $("#pontoon tbody tr").length,
          translated = $("#pontoon tbody tr.translated").length;
      $('#progress span').width(Math.round(translated*100 / all) + '%');
      $('#progress-value').html(translated + '/' + all);
    },
  
  
  
    /**
     * Attach event handlers
     */
    attachHandlers: function() {
      var self = this;
      
      // Update entities and progress when saved
      $(".editableToolbar > .save", this.client._doc).click(function() {
        var element = $(this).parent().get(0).target;
        self.updateEntity(element);
        self.updateProgress();
      });
  
      // Update progress when cancelled
      $(".editableToolbar > .cancel", this.client._doc).click(function() {
        self.updateProgress();
      });
  
      // Open/close Pontoon UI
      $('#switch').unbind("click.pontoon").bind("click.pontoon", function() {
        if ($('#pontoon').is('.opened')) {
          $('#entitylist').height(0);
        } else {
          $('#entitylist').height(300);
        }
        $('#source').height($(document).height() - $('#pontoon').height());
        $('#pontoon').toggleClass('opened');
      });
  
      // Selector box
      $('.selector').unbind("click.pontoon").bind("click.pontoon", function(e) {
        $(this).siblings('.menu').toggle();
        $(this).toggleClass('opened');
      });

      // Locale selector
      $('#locale-menu li:not(".add")').unbind("click.pontoon").bind("click.pontoon", function() {
        $('#flag').attr("class", $(this).find('span').attr("class"));
        $('#locale .selector .language').html($(this).find('.language').html());
        $('#locale .selector').click();
      });
      
      // Authentication
      $('#authentication-menu .restricted .go').unbind("click.pontoon").bind("click.pontoon", function() {
        var author = $('#nickname').val() || $('#email').val();
          $('#authentication .selector').click();
        if (author) {
          $('#authentication .author').html(author).toggleClass('authenticated');
          $('#authentication-menu, #save-menu').toggleClass('menu');
        }
      });

      // Authentication switch
      $('#authentication-menu .switch').unbind("click.pontoon").bind("click.pontoon", function() {
        $('#authentication-menu')
          .find('.wrapper').toggle().end()
          .find('#password').toggle();
      });

      // Save menu
      $('#save-menu').find('.sign-out').unbind("click.pontoon").bind("click.pontoon", function() {
        $('#authentication .selector').click();
        $('#authentication .author').html('Sign in').toggleClass('authenticated');
        $('#authentication-menu, #save-menu').toggleClass('menu');
      }).end().find('.server').unbind("click.pontoon").bind("click.pontoon", function() {
        $('#authentication .selector').click();
        self.save();
      });

    },
  
  
  
    /**
     * Show and render main UI
     * Enable editable text
     */
    renderTools: function() {
      $(this.client._data.entities).each(function() {
        if (this.node) { // For entities not found on the website
          this.node.editableText();
        }
      });
      this.attachHandlers();
      this.rebuildList();
    },
  
  
  
    /**
     * Update entity and main UI
     * 
     * element HTML Element which contains l10n entities
     */
    updateEntity: function(element) {
      var entity = element.entity,
          clone = $(element).clone();
  
      entity.translation = $(clone).html();
      entity.ui.find('textarea').text(entity.translation).parents('tr').addClass('translated');
    },
  
  
  
    /**
     * Extend entity object
     * 
     * e Temporary entity object
     */
    extendEntity: function(e) {
      e.original = e.original || ""; /* Original string */
      e.translation = e.translation || ""; /* Translated string */
      e.comment = e.comment || ""; /* Comment for localizers */
      e.node = e.node || null; /* HTML Element holding string */
      e.ui = e.ui || null; /* HTML Element representing string in the main UI */

      e.hover = function() {
        this.node.get(0).showToolbar();
        this.ui.toggleClass('hovered');
      };
      e.unhover = function() {
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
    guessEntities: function() {
      var self = this;
      this.client._data.entities = [];
  
      $(this.client._doc).find(':not("script, style")').contents().each(function() {
        if (this.nodeType === Node.TEXT_NODE && $.trim(this.nodeValue).length > 0 && $(this).parents(".pontoon-entity").length === 0) {
          var entity = {};
          entity.original = $(this).parent().html();
          entity.node = $(this).parent();
          self.extendEntity(entity);
          self.client._data.entities.push(entity);
          $(this).parent().addClass("pontoon-entity");
        }
      });
      
      $(".pontoon-entity").removeClass("pontoon-entity");
      self.renderTools();
    },
  
  
  
    /**
     * Get data from external meta file: original, translation, comment, suggestions...
     * Match with each string in the document, which is prepended with l10n comment nodes
     * Example: <!--l10n-->Hello World
     *
     * Create entity objects
     * Remove comment nodes
     */
    getEntities: function() {
      var self = this,
          prefix = 'l10n',
          counter = 1, /* TODO: use IDs or XPath */
          parent = null;

      $.getJSON($("#source").attr("src") + "/pontoon/sl.json").success(function(data) {
      	self.client._data = data;
      	var entities = self.client._data.entities;
      	
        $(self.client._doc).find('*').contents().each(function() {
          if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf(prefix) === 0) {
            var entity = entities[counter],
                translation = entity.translation;
            
            parent = $(this).parent();
            $(this).remove();
            if (translation.length > 0) {
              parent.html(translation);
            }

            entity.node = parent;
            self.extendEntity(entity);
            counter++;
          }
        });
        self.renderTools();
      });
    },
  
  

    /**
     * Extract entities from the document
     * Determine if the current page is prepared for working with Pontoon
     */ 
    extractEntities: function() {
      var meta = $(this.client._doc).find('head > meta[name=Pontoon]');
      if (meta.length > 0) {
        if (meta.attr('content')) {
          this.client._meta['project'] = meta.attr('content');
        }
        if (meta.attr('ip')) {
          this.client._meta['url'] = meta.attr('ip');
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
     */
    init: function(doc, ptn) {
      if (!doc) {
        throw "Document handler required";
      }
      
      // Build client object
      this.client = {
        _doc: doc,
        _ptn: ptn,
        _meta: {},
        _data: {}
      };
      
      // Enable document editing
      var ss = $('<link rel="stylesheet" href="../../client/lib/css/editable.css">', doc);
      $('head', doc).append(ss);      
      this.extractEntities();      
  
      // TODO: move to web client part of the code, selector should be on frontpage
      this.setLanguage();
    }

  };
}();
