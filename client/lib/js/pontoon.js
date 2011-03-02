var Entity = function(pc) {
  var _client = pc;
  this.string=null;
  this.txtString=null;
  // Translated String used in UI (text only), derived from this.translation
  this.txtTranslation=null;
  // Translated String used in PO file (may include HTML markup)
  this.translation=null;
  this.node=null;
  this.ui=null;
  this.id=null;
}

Entity.prototype = {
  '_client': null,
  'string': null,
  'txtString': null,
  'translation': null,
  'txtTranslation':null,
  'node': null,
  'ui': null,
  'id': null,
  
  hover: function() {
    this.node.get()[0].showToolbar();
    this.ui.toggleClass('hovered');
  },
  unhover: function() {
    this.node.get()[0].hideToolbar();
    this.ui.toggleClass('hovered');
  }
}

var PontoonService = function() {
}

PontoonService.prototype = {
  url: 'http://pontoon.server.ubuntu:8001/push/',
  send: function(pc) {
    var project = ('project' in pc._meta)?pc._meta['project']:pc._doc.location.href;
    var url = ('url' in pc._meta)?pc._meta['url']:'http://pontoon.server.ubuntu:8001/push/';
    var lang = $(pc._ptn).find('input').val();

    /*
     Pontoon server push expects a POST with the following properties
     id - list of msgid strings. The length of id should match the length of value
             Example: ['Hello World']
     value - list of msgstr - should be empty if no changes, otherwise set to the an edited value
             Example: ['Hallo Welt']
     project - url of the page being localized
     locale - locale msgstr are localized too
    */
    var data = { 'id': Array(), 
                 'value': Array(),
                 'project': project,
                 'locale': lang}
    var entities = Array();

    for(var i in pc._entities) {
      var entity = pc._entities[i];
      var trans = entity.translation?entity.translation:entity.string
      entities.push({'id':entity.string,'value':trans})
    }
    for (i in entities) {
      data['id'].push(entities[i].id)
      if (entities[i].id==entities[i].value)
        data['value'].push("")
      else
        data['value'].push(entities[i].value)      
    }
    $.ajaxSettings.traditional = true;
    $.post(url, data, null, "text");
  },
}

var PontoonUI = function() {}

PontoonUI.prototype = {
}

var Pontoon = {
  _clients: [],
  service: new PontoonService(),
  client: function(doc, ptn) {
    if (!doc)
      throw "Document handler required";
    this._doc = doc;
    this._ptn = ptn;
    this._entities = [];
    this._meta = {};
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

function trim(str) {
  return str.replace(/^\s+|\s+$/g, '')
}

Pontoon.L10N_PREFIX = 5;

Pontoon.client.prototype = {
  _doc: null,
  _ptn: null,
  _entities: null,
  _meta: {},
  _enchanted: null,

  /**
   * determine if the current page is "pontoon-enchanted"
   */ 
  isEnchanted: function() {
	if (this._enchanted == null) {
      var meta = $(this._doc).find('head > meta[name=Pontoon]');
      this._enchanted = (meta.size() > 0);
    }
    return this._enchanted;
  },

  /**
   * enables document editing
   */ 
  enableEditing: function() {
  	var ss = $('<link rel="stylesheet" href="../../client/lib/css/editable.css">', this._doc);
    $('head', this._doc).append(ss);
    this.extractEntities();
    for (var i in this._entities) {
      this._entities[i].node.editableText();
    }
  },

  /**
   * disables document editing
   */ 
  disableEditing: function() {
	$(this._doc).find('link').each(function() {
	  if ($(this).attr('href') == '../../client/lib/css/editable.css') {
		$(this).remove();	
	  }
	});
    for (var i in this._entities) {
      this._entities[i].node.disableEditableText();
    }
	$(this._doc).find('.editableToolbar').remove();
  },

  /**
   * extracts entities from the document
   */ 
  extractEntities: function(node) {
	if (this.isEnchanted()) {
      return this.extractEntitiesWithSpan(node);
    }
    return this.extractEntitiesWithGuessing(node);
  },

  /**
   * extracts entities from the document
   */ 
  extractEntitiesWithSpan: function(node) {
    this.extractAllEntities(this._doc);
  },
  /**
   * Extracts all gettext msgid and msgstr from the document.
   * Strings are wrapped in html10n comments.
   * Example: <!--l10n Hello World-->Hallo Welt<!--/l10n-->
   */
  extractAllEntities: function(document) {
    var inL10n = false;
    var self=this;
    var eles = document.getElementsByTagName('*');
    var entity;
    for (var elIndex=0; elIndex < eles.length; elIndex++) {
      var nodes = eles[elIndex].childNodes;
      for (var nodeIndex = 0; nodeIndex < nodes.length; nodeIndex++) {
        var node = nodes[nodeIndex];
        //Is this a Comment?
        if (node.nodeType == 8) {
          if (node.nodeValue.indexOf('l10n ') == 0) {
            
            if (window.consle && inL10n == true) {
              window.console.error("Already in l10n block, should never happen!");
            }
            inL10n = true;
            entity = new Entity(self);
            
            entity.string = node.nodeValue.substring(Pontoon.L10N_PREFIX);
            //entity.node will be the parentElement
            //entity.txtString will be the value of the next sibling node
            entity.id = entity.string;
            self._entities.push(entity);
            
          // Are we ending the html10n comment?
          } else if (node.nodeValue.indexOf('/l10n') == 0) {
            inL10n = false;
            entity = null;
          }
        // wasn't a Comment
        } else {
          if (inL10n && entity.node == null && node.nodeType == 3) {
            entity.node = $(node.parentNode);//Element
            entity.txtString = node.nodeValue;
          } // if (inL10n)
        }
      }
    }
  },
  /**
   * extracts entities from the document
   */ 
  extractEntitiesWithGuessing: function(node) {
    if (!node) {
      var node = $(this._doc.body);
    }
    var self = this;
    var nodeNames = ['P', 'H1', 'H2', 'LI', 'SPAN', 'A'];
    node.children().each(function() {
      if (this.nodeType === 3) { // text
        //if (trim(this.textContent))
        //alert(this.nodeValue);
      } else {
        var isInline = false;
        for (var i in nodeNames) {
          if (nodeNames[i] === this.nodeName) {
            isInline = true;
            var entity = new Entity(self);
            entity.node = $(this);
            entity.string = $(this).html();
            entity.txtString = $(this).text();
            if (!trim(entity.txtString)) {
              break;
            }
            self._entities.push(entity);
          }
        }
        if (!isInline) {
          self.extractEntities($(this));
        }
      }
    });
  },
  /**
   * element jQuery wrapped HTML Element which contains html10n nodes
   */
  updateEntities: function(element) {
    // entity is an HTML Element, however... it contains one or more
    // Nodes which are marked html10n...
    //
    var entity = element.entity;
    var inL10n = false;

    // Is this a Comment?
    // TODO: not tested yet
    for (var nodeIndex = 0; nodeIndex < element.childNodes.length; nodeIndex++) {
      var node = element.childNodes[nodeIndex];
      if (node.nodeType === 8) {
        if (node.nodeValue.indexOf('l10n ') === 0) {
          // Is this html10n comment the one we're looking for?
          var msgid = node.nodeValue.substring(5);
          if (msgid === entity.id) {            
            inL10n = true;
            entity.translation = "";
            entity.txtTranslation = "";
          } 
        } else if (node.nodeValue.indexOf('/l10n') === 0) {
          inL10n = false;            
        }
      }
    }
    
    entity.translation = $(element).html();
    entity.txtTranslation = $(element).text();
    entity.ui.find('textarea').text(entity.translation)
      
  },
  send: function() {
    Pontoon.service.send(this);
  },
  /**
   * Initialize Pontoon Client
   */
  turnOn: function(pc, doc) {
    this.enableEditing();

    // Show and render main UI
    this.attachHandlers(pc, doc);    
    this.rebuildUIList(pc);
    $('#pontoon').slideDown();
  },
  /**
   * Attach event handlers to Pontoon header element
   */
  attachHandlers: function(pc, doc) {
    // Update entities when saved
    $(".editableToolbar > .save", doc).click(function() {
      var element = $(this).parent().get(0).target;
      pc.updateEntities(element);
    });

    // Open/close Pontoon UI
    $('#switch, #logo').unbind("click.pontoon").bind("click.pontoon", function() {
      if ($('#pontoon').is('.opened')) {
        $('#entitylist').slideUp(function() {
          $('#source').height($(document).height() - $('#pontoon').height());
        });
      } else {
        $('#entitylist').slideDown(function() {
          $('#source').height($(document).height() - $('#pontoon').height());
        });
      }
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
      Pontoon._clients[0].send();
    });
  },
  /**
   * Render source - translation pairs
   */
  rebuildUIList: function(pc) {
    var list = $(pc._ptn).find('#entitylist').empty()
        // tables still need 'cellspacing="0"' in the markup: http://meyerweb.com/eric/thoughts/2007/05/01/reset-reloaded/
        .append('<table cellspacing="0"><thead><tr><th>Source</th><th>Translation</th></tr></thead><tbody></tbody></table>'),
        i = 0;

	$.each(pc._entities, function(i, entity) {
      var tr = $('<tr><td class="source"><p>' + entity.txtString + '</p></td><td class="translation"><textarea>' + entity.string + '</textarea></td></tr>', pc._ptn);
          
      tr.get(0).entity = entity;
      entity.node.get(0).entity = entity;
      entity.ui = tr;

      list.find('tbody').append(tr);
	});

    $("#pontoon tr").hover(function() {
      this.entity.hover();
    }, function() {
      this.entity.unhover();
    }).click(function() {
      $(pc._doc).find('.editableToolbar > .edit').click();
    });
  }

}
