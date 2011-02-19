/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is Pontoon.
 *
 * The Initial Developer of the Original Code is
 * Frederic Wenzel <fwenzel@mozilla.com>.
 * Portions created by the Initial Developer are Copyright (C) 2009
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

'use strict';
(function ($) {

    // DOMEC Core class
    $.DOMEC = (function () {
        // variables declaration
        // DOM element
        var Element = (function () {
            return {
                // create element
                create: function (name, root) {
                    // set default root if undefined
                    if (root === undefined || root === null) {
                        root = document;
                    }

                    if (typeof root === 'object' && !$.isArray(root) && 
                        typeof name === 'string') {
                        return $(root.createElement(name));
                    }

                    return undefined;
                },
                
                // add attributes
                addAttributes: function (elem, attr) {
                    if (typeof attr === 'object' && attr !== null && !$.isArray(attr)) {
                        $.each(attr, function (key, val) {
                            if (typeof val === 'string' || typeof val === 'number') {
                                elem.attr(key, val);
                            }
                        });
                    }
                },
                
                // add event handlers
                addEventHandlers: function (elem, events) {
                    if (typeof events === 'object' && events !== null && !$.isArray(events)) {
                        $.each(events, function (key, val) {
                            if (typeof key === 'string' && typeof val === 'function') {
                                elem.bind(key, val);
                            }
                        });
                    }
                },
                
                // add child elements
                addChildren: function (elem, children) {
                    if (children !== undefined && children !== null) {
                        if ($.isArray(children)) {
                            $.each(children, function (i, value) {
                                elem.append(value);
                            });
                        } else if (children instanceof jQuery) {
                            elem.append(children);
                        } else {
                            elem.text(children.toString());
                        }
                    }
                }
            };
        }());

        // DOMEC public members
        return {
            create: function (name, options) {
            
                var elem;
                
                if (typeof options === 'object' && options !== null && !$.isArray(options) &&
                    options.hasOwnProperty('root')) {
                    elem = Element.create(name, options.root);
                } else {
                    elem = Element.create(name);
                }

                if (elem !== undefined && typeof options === 'object' && options !== null && 
                    !$.isArray(options)) {
                    if (options.hasOwnProperty('attributes')) {
                        Element.addAttributes(elem, options.attributes);
                    }
                    
                    if (options.hasOwnProperty('events')) {
                        Element.addEventHandlers(elem, options.events);
                    }
                    
                    if (options.hasOwnProperty('children')) {
                        Element.addChildren(elem, options.children);
                    }
                }

                return elem;
            }
        };
    }());

    // register jQuery extension
    $.extend({
        create: $.DOMEC.create
    });

}(jQuery));

/**
 * editableText plugin that uses contentEditable property (FF2 is not supported)
 * Project page - http://github.com/valums/editableText
 * Copyright (c) 2009 Andris Valums, http://valums.com
 * Licensed under the MIT license (http://valums.com/mit-license/)
 */
 (function(){
      /**
       * The dollar sign could be overwritten globally,
       * but jQuery should always stay accesible
       */
      var $ = jQuery;
      /**
       * Extending jQuery namespace, we
       * could add public methods here
       */
      $.editableText = {};
      $.editableText.defaults = {         
          /**
           * Pass true to enable line breaks.
           * Useful with divs that contain paragraphs.
           */
          newlinesEnabled : false,
          /**
           * Event that is triggered when editable text is changed
           */
          changeEvent : 'change'
      };           
      /**
       * Usage $('selector).editableText(optionArray);
       * See $.editableText.defaults for valid options 
       */        
      $.fn.editableText = function(options){
          var options = $.extend({}, $.editableText.defaults, options);
          var doc = this.get()[0].ownerDocument;
          var body = $(doc.body);

          // Create edit/save buttons
          function showToolbar(elem) {
              if ($(elem).attr('class')=='editableToolbar') {
                var toolbar = $(elem);
                var curTarget =  toolbar.get()[0].target
                var newTarget = null;
                curTarget.entity.hover()
                return true;
              } else {       
                var body = $($(elem).get()[0].ownerDocument.body); 
                var win = $(elem).get()[0].ownerDocument.defaultView;
                var toolbar = body.find('.editableToolbar')
                var curTarget =  toolbar.get()[0].target
                var newTarget = elem;
                if ($(curTarget).attr('contentEditable')=='true')
                    return;
                if (curTarget && curTarget!=newTarget) {
                  hideToolbar(curTarget);
                }
                var left = newTarget.getBoundingClientRect().left+win.scrollX
                var top = newTarget.getBoundingClientRect().top+win.scrollY
                toolbar.css('left', left+'px')
                toolbar.css('top', top-20+'px')
              }           
              var toolbarNode = toolbar.get()[0]
              if(toolbarNode.I!==null) {
                clearTimeout(toolbarNode.I)
                toolbarNode.I = null;
              }
              if (newTarget)
                toolbarNode.target=newTarget;
              $(newTarget).addClass('hovered')
              toolbar.css('display', 'block')
          }

          function hideToolbar(elem) {
            if ($(elem).attr('class')=='editableToolbar') {
                var toolbar = $(elem);
            } else {
              var body = $($(elem).get()[0].ownerDocument.body); 
              var toolbar = body.find('.editableToolbar')
            }
            var toolbarNode = toolbar.get()[0]
            var target = toolbarNode.target
            if ($(target).attr('contentEditable')=='true')
              return;
            function hide() {
              if (target) {
                target.blur();
                stopEditing(toolbar);
                if (target==toolbar.get()[0].target) {
                  toolbar.get()[0].target=null;
                  $(target).removeClass('hovered')
                  toolbar.css('display', 'none')
                } else {
                  $(target).removeClass('hovered')
                }
              }
            }
            toolbar.get()[0].I = setTimeout(hide, 50);
          }

          /**
           * Makes element editable
           */
          function startEditing(toolbar){
              toolbar.children().css('display','inline');
              toolbar.find('.edit').css('display','none');
              $(toolbar.get()[0].target).attr('contentEditable', true);
              toolbar.get()[0].target.focus()
          }
          /**
           * Makes element non-editable
           */
          function stopEditing(toolbar){
              toolbar.children().css('display','none');
              toolbar.find('.edit').css('display','inline');
              $(toolbar.get()[0].target).attr('contentEditable', false);
          }
          if (!body.find('.editableToolbar').length) {
            var toolbar = $(
                  "<div class='editableToolbar'>" +
                        "<a href='#' class='edit'></a>" +
                    "<a href='#' class='save'></a>" +
                    "<a href='#' class='cancel'></a>" +
                "</div>", doc).appendTo(body);
            toolbar.hover(function() {
              showToolbar(this);
            },function() {
             this.target.entity.unhover()
            })

            // Save references and attach events            
            var editEl = toolbar.find('.edit').click(function() {
                startEditing(toolbar);
                return false;
            });                            

            toolbar.find('.save').click(function(){
                stopEditing(toolbar);
                //editable.trigger(options.changeEvent);
                return false;
            });

            toolbar.find('.cancel').click(function(){
                stopEditing(toolbar);
                var target = toolbar.get()[0].target
                $(target).html(target.prevValue);
                target.entity.string=target.prevValue
                target.entity.ui.text(shorten(target.txtPrevValue))
                return false;
            });        
            // Display only edit button            
            toolbar.children().css('display', 'none');
            editEl.show();

          }
          return this.each(function(){
               // Add jQuery methods to the element
              var editable = $(this);

              /**
               * Save value to restore if user presses cancel
               */
              this.prevValue = editable.html().toString();
              this.txtPrevValue = editable.text().toString();
              this.showToolbar = function(){showToolbar(this)}
              this.hideToolbar = function(){hideToolbar(this)}
              editable.hover(function() {
                this.entity.hover();
              },function() {
                this.entity.unhover();
              })

              if (!options.newlinesEnabled){
                  // Prevents user from adding newlines to headers, links, etc.
                  editable.keypress(function(event){
                      // event is cancelled if enter is pressed
                      return event.which != 13;
                  });
              }

          });
      }
      $.fn.disableEditableText = function(options){
          return this.each(function(){
               // Add jQuery methods to the element
              var editable = $(this);
              this.prevValue = undefined;
              this.txtPrevValue = undefined;
              this.showToolbar = undefined;
              this.hideToolbar = undefined;
              $(this).unbind('mouseenter mouseleave keypress');
          });
      }
  })();

// imports
jetpack.future.import("slideBar");

// central hooks
addPontoonSlidebar();

/**
 * add the main Pontoon slidebar
 */
function addPontoonSlidebar(doc) {
  jetpack.slideBar.append({
    width: 300,
    persist: true,
    autoReload: false,
    onReady: function(slide) {
      jetpack.tabs.onReady(function() {
        disablePontoon();
      });
      jetpack.tabs.onFocus(function() {
        disablePontoon();
      });
	  var ptn = slide.contentDocument,
	      $ptn = $(ptn),
	      doc = jetpack.tabs.focused.contentDocument,
	      $doc = $(doc);
	  $ptn.find('#send').click(function() {Pontoon._clients[0].send()});
	  $ptn.find('#enableEditing').click(function() {redrawPontoon(slide)});
	  $ptn.find('#disableEditing').click(function() {disablePontoon()});
    },
    onClick: function(slide) {
	  //redrawPontoon(slide);
    },
    onUnload: function(slide) {
	  Pontoon._clients[0].disableEditing();
    },
    html: <>
      <style><![CDATA[
      body {
        background-color: #fff;
        font-family: sans-serif;
        font-size: 10pt;
      }
      ul {
        list-style-type: none;
        margin:0;
        padding: 0;
        margin-top: 10px;
        border: 1px solid #eee;
      }

      ul li {
        display: block;
        padding: 5px 5px;
        border-bottom: 1px solid #eee;
        font-size: 0.8em;
      }
      ul li.hovered {
        text-decoration: underline;
        background-color: #eee;
        cursor: pointer;
      }
      ]]></style>
      <body>
        <h1>Welcome to Pontoon!</h1>
        <p class="type"></p>
        <div id="operate">
          <button id="enableEditing">Enable editing</button>
          <button id="disableEditing">Disable editing</button>
        </div>
        <div class="content">
          <p>This is a list of elements that can be translated on this page. Hover over any of them to see them highlighted.</p>
          <p>To translate a string, simply click on it.</p>
          <label>Locale:</label>
          <input type="text" id="locale" value="fr" style="width:50px"/>
          <ul id="list"></ul>
        </div>
        <button id="send">Send it</button>
      </body>
    </>
  });
}

function disablePontoon() {
  if (Pontoon._clients.length) {
    Pontoon._clients[0].disableEditing();
    Pontoon._clients[0]._entities = [];
    rebuildUIList(Pontoon._clients[0]);
    Pontoon._clients = [];
  }
}

function redrawPontoon(slide) {
  var ptn = slide.contentDocument,
      $ptn = $(ptn),
      doc = jetpack.tabs.focused.contentDocument,
      $doc = $(doc);

  if(Pontoon._clients.length==0) {
    var pc = new Pontoon.client(doc, ptn);
    if (pc.isEnchanted()) {
	  $ptn.find('p.type').text('This page is pontoon enchanted');
	} else {
	  $ptn.find('p.type').text('This page is not pontoon enchanted');
	}
	turnOn(pc, doc);
	rebuildUIList(pc);
  }
}

function turnOn(pc, doc) {
  pc.enableEditing();
  $(".editableToolbar > .save", doc).click(function() {
    var editable = $($(this).parent().get()[0].target)
    var entity = editable.get()[0].entity
    entity.translation = editable.html().toString();
    entity.txtTranslation = editable.text().toString();
    entity.ui.text(shorten(entity.txtTranslation))
  })
}

/**
 * shorten an string
 */
function shorten(text, maxlen) {
  if (!maxlen) maxlen = 50;

  if (text.length <= maxlen) return text;
  return text.substr(0, maxlen-4)+new String(' ...');
}

function rebuildUIList(pc) {
  var ul = $(pc._ptn).find('#list');
  ul.empty();
  for (var i in pc._entities) {
    var entity = pc._entities[i];
    var str = entity.txtString;
    var li = $.create('li', {'children': shorten(str), 'root': pc._ptn});
    li.get()[0].entity = entity;
    li.hover(function() {
      this.entity.hover();
    },function() {
      this.entity.unhover();
    });
    li.click(function() {
      $(pc._doc).find('.editableToolbar > .edit').click()
    })
    entity.node.get()[0].entity = entity
    entity.ui = li;
    ul.append(li);
  }
}

/////////////////////////////////////////////////////////////////
function alert(msg) {
	jetpack.notifications.show({
      title: "Alert",
      body: msg
    });
}

var Entity = function(pc) {
  var _client = pc;
  this.string=null;
  this.txtString=null;
  this.txtTranslation=null;
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
  url: 'http://127.0.0.1:8000/push/',
  send: function(pc) {
    var project = ('project' in pc._meta)?pc._meta['project']:pc._doc.location.href;
    var url = ('url' in pc._meta)?pc._meta['url']:'http://127.0.0.1:8000/push/';
    var lang = $(pc._ptn).find('input').val();

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
    var ss = $.create('link', {'attributes': {'rel': 'stylesheet',
                                              'type': 'text/css',
                                              'media': 'screen',
                                              'href': 'http://pontoon.haskwhal/client/www/css/editable.css'},
                              'root': this._doc});
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
	  if ($(this).attr('href') == 'http://pontoon.haskwhal/client/www/css/editable.css') {
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
	if (this.isEnchanted())
      return this.extractEntitiesWithSpan(node);
    return this.extractEntitiesWithGuessing(node);
  },

  /**
   * extracts entities from the document
   */ 
  extractEntitiesWithSpan: function(node) {
	  // make list of translatable items
      if (!node)
        var node = $(this._doc.body);
	  var translatable = $(node).find('span.l10n');
	  var self=this;
	  translatable.each(function() {
        var entity = new Entity(self);
        entity.node = $(this)
        entity.string = $(this).html().toString()
        entity.txtString = $(this).text().toString()
	    entity.id = /md5_([a-zA-Z0-9]+)/.exec($(this).attr('class'))[1];
        self._entities.push(entity);
	  });
  },

  /**
   * extracts entities from the document
   */ 
   extractEntitiesWithGuessing: function(node) {
     if (!node)
       var node = $(this._doc.body);
     var self=this;
     var nodeNames = ['P','H1','H2','LI','SPAN','A']
     node.children().each(function() {
       if (this.nodeType == 3) { // text
         //if (trim(this.textContent))
         //alert(this.nodeValue);
       } else {
         var isInline = false;
         for (var i in nodeNames)
           if(nodeNames[i]==this.nodeName) {
             isInline = true;
             var entity = new Entity(self);
             entity.node = $(this)
             entity.string = $(this).html().toString()
             entity.txtString = $(this).text().toString()
             if (!trim(entity.txtString))
                 break;
             self._entities.push(entity);
           }
         if(!isInline)
           self.extractEntities($(this));
       }
     });
   },

  send: function() {
    Pontoon.service.send(this);
  },
}