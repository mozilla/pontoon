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
        newlinesEnabled: false,
        /**
         * Event that is triggered when editable text is changed
         */
        changeEvent: 'change'
      };           
      /**
       * Usage $('selector).editableText(optionArray);
       * See $.editableText.defaults for valid options 
       */        
      $.fn.editableText = function(options){
          var options = $.extend({}, $.editableText.defaults, options),
              doc = this.get(0).ownerDocument,
              body = $(doc.body);

          // Create edit/save buttons
          function showToolbar(elem) {
            if ($(elem).attr('class') === 'editableToolbar') {
              var toolbar = $(elem),
                  curTarget =  toolbar.get(0).target,
                  newTarget = null;
              curTarget.entity.hover();
              return true;
            } else {       
              var body = $($(elem).get(0).ownerDocument.body),
                  win = $(elem).get(0).ownerDocument.defaultView,
                  toolbar = body.find('.editableToolbar'),
                  curTarget =  toolbar.get(0).target,
                  newTarget = elem;
              if ($(curTarget).attr('contentEditable') === 'true') {
                return;
              }
              if (curTarget && curTarget !== newTarget) {
                hideToolbar(curTarget);
              }
              var left = newTarget.getBoundingClientRect().left + win.scrollX,
                  top = newTarget.getBoundingClientRect().top + win.scrollY;
              toolbar.css('left', left + 'px')
                     .css('top', top-21 + 'px');
            }           
            var toolbarNode = toolbar.get(0);
            if (toolbarNode.I !== null) {
              clearTimeout(toolbarNode.I);
              toolbarNode.I = null;
            }
            if (newTarget) {
              toolbarNode.target = newTarget;
            }
            $(newTarget).addClass('hovered');
            toolbar.css('display', 'block');
          }

          function hideToolbar(elem) {
            if ($(elem).attr('class') === 'editableToolbar') {
              var toolbar = $(elem);
            } else {
              var body = $($(elem).get(0).ownerDocument.body),
                  toolbar = body.find('.editableToolbar');
            }
            var toolbarNode = toolbar.get(0),
                target = toolbarNode.target;
            if ($(target).attr('contentEditable') === 'true') {
              return;
            }
            function hide() {
              if (target) {
                target.blur();
                stopEditing(toolbar);
                if (target === toolbar.get(0).target) {
                  toolbar.get(0).target = null;
                  $(target).removeClass('hovered');
                  toolbar.css('display', 'none');
                } else {
                  $(target).removeClass('hovered');
                }
              }
            }
            toolbar.get(0).I = setTimeout(hide, 50);
          }

          /**
           * Makes element editable
           */
          function startEditing(toolbar) {
            toolbar.children().css('display','inline');
            toolbar.find('.edit').css('display','none');
            var target = toolbar.get(0).target;
            $(target).attr('contentEditable', true);
            target.focus();
            $(target.entity.ui).addClass("active");
          }
          /**
           * Makes element non-editable
           */
          function stopEditing(toolbar) {
            toolbar.children().css('display','none');
            toolbar.find('.edit').css('display','inline');
            var target = toolbar.get(0).target;
            $(target).attr('contentEditable', false);
            $(target.entity.ui).removeClass("active");
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

            toolbar.find('.save, .cancel').click(function(){
                stopEditing(toolbar);
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
