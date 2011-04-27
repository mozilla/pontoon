// TODO: do we need to separate markup and text?
var Entity = function(pc) {
  var _client = pc;
  this.string = null; /* Original string used in PO file (may include HTML markup) */
  this.txtString = null; /* Original string used in UI (text only), derived from this.string */
  this.translation = null; /* Translated string used in PO file (may include HTML markup) */
  this.txtTranslation = null; /* Translated string used in UI (text only), derived from this.translation */
  this.node = null; /* HTML Element holding string */
  this.ui = null; /* HTML Element representing string in the main UI */
  this.id = null;
}

Entity.prototype = {
  '_client': null,
  'string': null,
  'txtString': null,
  'translation': null,
  'txtTranslation': null,
  'node': null,
  'ui': null,
  'id': null,
  
  hover: function() {
    this.node.get(0).showToolbar();
    this.ui.toggleClass('hovered');
  },
  unhover: function() {
    this.node.get(0).hideToolbar();
    this.ui.toggleClass('hovered');
  }
}

var PontoonService = function() {
}

PontoonService.prototype = {
  url: 'http://pontoon.server.ubuntu:8001/push/',

  /*
   * Pontoon server push expects a POST with the following properties:
   *
   * id - list of msgid strings. The length of id should match the length of value ['Hello World']
   * value - list of msgstr - should be empty if no changes, otherwise set to the an edited value ['Hallo Welt']
   * project - url of the page being localized
   * locale - locale msgstrs are localized too
  */
  send: function(pc) {
    var project = ('project' in pc._meta) ? pc._meta['project'] : pc._doc.location.href,
        lang = $(pc._ptn).find('input').val(),
        data = {
          'id': [], 
          'value': [],
          'project': project,
          'locale': lang
        },
        entities = [],
        url = ('url' in pc._meta) ? pc._meta['url'] : 'http://pontoon.server.ubuntu:8001/push/';
    
    $(pc._entities).each(function() {
      var entity = this,
          trans = entity.translation ? entity.translation : entity.string;
      entities.push({
        'id': entity.string,
        'value': trans
      })
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
}

var Pontoon = {
  _clients: [],
  service: new PontoonService(),
  client: function(doc, ptn) {
    if (!doc) {
      throw "Document handler required";
    }
    this._doc = doc,
    this._ptn = ptn,
    this._entities = [],
    this._meta = {},
    this._enchanted = null;

	var meta = $(doc).find('head > meta[name=Pontoon]');
	if (meta.attr('content'))
	  this._meta['project'] = meta.attr('content');
	var meta = $(doc).find('head > meta[name=Pontoon]');
	if (meta.attr('ip'))
	  this._meta['url'] = meta.attr('ip');
    Pontoon._clients.push(this);
  },
}

Pontoon.L10N_PREFIX = 5;

Pontoon.client.prototype = {
  _doc: null,
  _ptn: null,
  _entities: null,
  _meta: {},
  _enchanted: null,



  /**
   * Send data to server
   */
  send: function() {
    Pontoon.service.send(this);
  },



  /**
   * Build source - translation pairs
   */
  rebuildUIList: function(pc) {
    var list = $(pc._ptn).find('#entitylist').empty()
        // tables still need 'cellspacing="0"' in the markup
        // http://meyerweb.com/eric/thoughts/2007/05/01/reset-reloaded/
        .append('<table cellspacing="0"><thead><tr><th>Source</th><th>Translation</th></tr></thead><tbody></tbody></table>');

    // Render
	$(pc._entities).each(function() {
      var tr = $('<tr><td class="source"><p>' + this.txtString + '</p><ul class="tools"><li title="Copy original string to translation" class="copy"></li><li title="Machine translation by Google Translate" class="auto-translate"></li><li title="Comment" class="comment"></li></ul></td><td class="translation"><div class="suggestions"><a href="#translation" class="translation active">Translation</a><a href="#translation-memory" class="tm">Translation memory</a><a href="#other-users" class="users">Other users</a><a href="#other-locales" class="locales">Other locales</a></div><textarea>' + (this.translation || '') + '</textarea></td></tr>', pc._ptn);
          
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
      $(pc._doc).find('.editableToolbar > .edit').click();
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
  attachHandlers: function(pc) {
    // Update entities and progress when saved
    $(".editableToolbar > .save", this._doc).click(function() {
      var element = $(this).parent().get(0).target;
      pc.updateEntities(element);
      pc.updateProgress();
    });

    // Update progress when cancelled
    $(".editableToolbar > .cancel", this._doc).click(function() {
      pc.updateProgress();
    });

    // Open/close Pontoon UI
    $('#switch, #logo').unbind("click.pontoon").bind("click.pontoon", function() {
      $('#entitylist').toggle();
      $('#source').height($(document).height() - $('#pontoon').height());
      $('#pontoon').toggleClass('opened');
    });

    // Locale selector
    $('#locale').unbind("click.pontoon").bind("click.pontoon", function() {
      $('#locale-list').css("left", $("#locale").position().left).toggle();
      $(this).toggleClass('opened');
    });
    $('#locale-list li').unbind("click.pontoon").bind("click.pontoon", function() {
      $('#flag').attr("class", $(this).find('span').attr("class"));
      $('#locale .language').html($(this).find('.language').html());
      $('#locale').click();
    });

    // Send changes to server
    $("#send").click(function () {
      pc.send();
    });
  },



  /**
   * Update entity and main UI
   * 
   * element HTML Element which contains html10n nodes
   */
  updateEntities: function(element) {
    var entity = element.entity,
        clone = $(element).clone();

    entity.translation = $(clone).html();
    entity.txtTranslation = $(clone).text();
    entity.ui.find('textarea').text(entity.translation).parents('tr').addClass('translated');
  },



  /**
   * Extract entities from the document
   * Create entity from every non-empty text node
   */ 
  guessEntities: function() {
    var self = this,
        entity = null;

    $(this._doc).find(':not("script, style")').contents().each(function() {
      if (this.nodeType === Node.TEXT_NODE && $.trim(this.nodeValue).length > 0) {
        entity = new Entity(self);
        entity.string = entity.txtString = entity.translation = entity.txtTranslation = entity.id = this.nodeValue;
        entity.node = $(this).parent();
        self._entities.push(entity);

        $(this).parent().attr("data-l10n", entity.string);
      }
    });    
  },



  /**
   * Extract all gettext msgid and msgstr from the document
   * Strings are prepended with l10n comment nodes
   * Example: <!--l10n Hello World-->Hallo Welt
   *
   * Create entity object from comment and the text node that follows
   * Move comment node contents to the parent's element data-l10n attribute
   * Remove comment nodes
   */
  parseEntities: function() {
    var self = this,
        entity = null;

    $(this._doc).find('*').contents().each(function() {
      if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf('l10n ') === 0) {
        entity = new Entity(self);
        entity.string = entity.txtString = entity.id = this.nodeValue.substring(Pontoon.L10N_PREFIX);
        entity.translation = entity.txtTranslation = $(this.nextSibling).text();
        entity.node = $(this).parent();
        self._entities.push(entity);

        $(this).parent().attr("data-l10n", entity.string);
        $(this).remove();
      }
    });
  },



  /**
   * Determine if the current page is prepared for working with Pontoon
   */ 
  isEnchanted: function() {
	if (this._enchanted === null) {
      this._enchanted = ($(this._doc).find('head > meta[name=Pontoon]').length > 0);
    }
    return this._enchanted;
  },



  /**
   * Extract entities from the document
   */ 
  extractEntities: function() {
	if (this.isEnchanted()) {
      return this.parseEntities();
    }
    return this.guessEntities();
  },



  /**
   * Disable document editing
   */ 
  disableEditing: function() {
    $(this._doc).find('link[href="../../client/lib/css/editable.css"]').each(function() {
      $(this).remove();
    });
    $(this._entities).each(function() {
      this.node.disableEditableText();
    });
	$(this._doc).find('.editableToolbar').remove();
  },



  /**
   * Enable document editing
   */ 
  enableEditing: function() {
  	var ss = $('<link rel="stylesheet" href="../../client/lib/css/editable.css">', this._doc);
    $('head', this._doc).append(ss);
    this.extractEntities();
    $(this._entities).each(function() {
      this.node.editableText();
    });
  },



  /**
   * Initialize Pontoon Client
   */
  turnOn: function(pc) {
    this.enableEditing();

    // Show and render main UI
    this.attachHandlers(pc);    
    this.rebuildUIList(pc);
    $('#pontoon').slideDown();
  }
}
