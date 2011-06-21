var Pontoon = function() {

  /* public  */
  return {



    /*
     * Send data to server
     * Pontoon server push expects a POST with the following properties:
     *
     * id - list of msgid strings, the length of id should match the length of value ['Hello World']
     * value - list of msgstrs, should be empty if no changes, otherwise set to the edited value ['Hallo Welt']
     * project - url of the page being localized
     * locale - locale msgstrs are localized too
    */
    send: function() {
      var project = ('project' in this.client._meta) ? this.client._meta['project'] : this.client._doc.location.href,
          lang = $(this.client._ptn).find('input').val(),
          data = {
            'id': [], 
            'value': [],
            'project': project,
            'locale': lang
          },
          entities = [],
          url = ('url' in this.client._meta) ? this.client._meta['url'] : 'http://127.0.0.1:8000/push/';
      
      $(this.client._entities).each(function() {
        var entity = this,
            trans = entity.translation ? entity.translation : entity.original;
        entities.push({
          'id': entity.original,
          'value': trans
        });
      });
      
      $(entities).each(function() {
        data['id'].push(this.id);
        if (this.id === this.value) {
          data['value'].push("");
        } else {
          data['value'].push(this.value);
        }
      });
  
      $.ajaxSettings.traditional = true;
      $.post(url, data, null, "text");
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
      $.ajax({ 
        url: "http://ajaxhttpheaders.appspot.com", 
        dataType: 'jsonp', 
        success: function(headers) {
          var language = headers['Accept-Language'].substring(0, 2),
              entry = $('#locale-list .flag.' + language);
          if (entry.length !== 0) {
            $('#flag').addClass(language);
            $('#locale .language').html(entry.next().text());
          }
        }
      }).done(function() {
        $('#pontoon').slideDown();
      });
    },



    /**
     * Build source - translation pairs
     */
    rebuildList: function() {
      var self = this,
          list = $(this.client._ptn).find('#entitylist').empty()
          // tables still need 'cellspacing="0"' in the markup
          // http://meyerweb.com/eric/thoughts/2007/05/01/reset-reloaded/
          .append('<table cellpadding="0" cellspacing="0" border="0"><thead><tr><th>Source</th><th>Translation</th></tr></thead><tbody></tbody></table>');
  
      // Render
      $(this.client._entities).each(function() {
        var tr = $('<tr' + (this.translation ? ' class="translated"' : '') + '><td class="source"><p>' + this.original + '</p><ul class="tools"><li title="Copy original string to translation" class="copy"></li><li title="Machine translation by Google Translate" class="auto-translate"></li><li title="Comment" class="comment"></li></ul></td><td class="translation"><div class="suggestions"><a href="#translation" class="translation active">Translation</a><a href="#translation-memory" class="tm">Translation memory</a><a href="#other-users" class="users">Other users</a><a href="#other-locales" class="locales">Other locales</a></div><textarea>' + (this.translation || '') + '</textarea></td></tr>', self.client._ptn);
            
        tr.get(0).entity = this;
        this.node.get(0).entity = this;
        this.ui = tr;
  
        list.find('tbody').append(tr);
      });
  
      // Event handlers
      $("#pontoon tr").hover(function() {
        this.entity.hover();
      }, function() {
        this.entity.unhover();
      }).click(function() {
        $(self.client._doc).find('.editableToolbar > .edit').click();
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
  
      // Locale selector
      $('#locale').unbind("click.pontoon").bind("click.pontoon", function() {
        $('#locale-list').css("left", $("#flag").position().left - 12).toggle();
        $(this).toggleClass('opened');
      });
      $('#locale-list li:not(".add")').unbind("click.pontoon").bind("click.pontoon", function() {
        $('#flag').attr("class", $(this).find('span').attr("class"));
        $('#locale .language').html($(this).find('.language').html());
        $('#locale').click();
      });
  
      // Send changes to server
      $("#send").click(function () {
        self.send();
      });
    },
  
  
  
    /**
     * Show and render main UI
     * Enable editable text
     */
    renderTools: function() {
      $(this.client._entities).each(function() {
        this.node.editableText();
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
     * Create entity object
     */
    createEntity: function(e) {
      var entity = {
        original: e.original || null, /* Original string used in PO file (may include HTML markup) */
        translation: e.translation || null, /* Translated string used in PO file (may include HTML markup) */
        node: e.node || null, /* HTML Element holding string */
        ui: e.ui || null, /* HTML Element representing string in the main UI */
        id: e.id || null,      
        _client: this,

        hover: function() {
          this.node.get(0).showToolbar();
          this.ui.toggleClass('hovered');
        },
        unhover: function() {
          this.node.get(0).hideToolbar();
          this.ui.toggleClass('hovered');
        }
      }
      
      this.client._entities.push(entity);
    },
  
  
  
    /**
     * Extract entities from the document, not prepared for working with Pontoon
     * 
     * Create entity object from every non-empty text node
     * Exclude nodes from special tags, e.g. <script> and <link>
     * Skip nodes already included in parent nodes
     */ 
    guessEntities: function() {
      var self = this;
  
      $(this.client._doc).find(':not("script, style")').contents().each(function() {
        if (this.nodeType === Node.TEXT_NODE && $.trim(this.nodeValue).length > 0 && $(this).parents(".pontoon-entity").length === 0) {
          var entity = {};
          entity.original = entity.translation = entity.id = $(this).parent().html();
          entity.node = $(this).parent();
          self.createEntity(entity);
          
          // Add temporary pontoon-entity class to prevent duplicate entities when guessing 
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
          parent = null,
          translation = "";

      $.getJSON($("#source").attr("src") + "/sl.json").success(function(data) {
        $(self.client._doc).find('*').contents().each(function() {
          if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf(prefix) === 0) {
            var entity = {};
            entity.original = entity.id = data.entity[counter].original;

            parent = $(this).parent();
            $(this).remove();

            translation = data.entity[counter].translation;
            if (translation.length > 0) {
              entity.translation = translation;
              parent.html(translation);
            }
            entity.node = parent;
            self.createEntity(entity);
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
     */
    init: function(doc, ptn) {
      if (!doc) {
        throw "Document handler required";
      }
      
      // Build client object
      this.client = {
        _doc: doc,
        _ptn: ptn,
        _entities: [],
        _meta: {}
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
