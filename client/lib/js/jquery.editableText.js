/**
* editableText plugin that uses contentEditable property
* Copyright (c) 2009 Andris Valums, http://valums.com
* Licensed under the MIT license (http://valums.com/mit-license/)
*/
(function(){
  // The dollar sign could be overwritten globally, but jQuery should always stay accesible
  var $ = jQuery;

  // Usage $('selector).editableText(optionArray);
  $.fn.editableText = function(){

    // Show toolbar
    function showToolbar(element) {
      if ($(element).is('.editableToolbar')) {
        $(element).get(0).target.entity.hover();
        return true;
      } else {       
        var toolbar = $('.editableToolbar'),
            curTarget = toolbar.get(0).target,
            newTarget = element;
        if ($(curTarget).attr('contentEditable') === 'true') {
          return;
        }
        if (curTarget && curTarget !== newTarget) {
          hideToolbar(curTarget);
        }
        var left = newTarget.getBoundingClientRect().left + window.scrollX,
            top = newTarget.getBoundingClientRect().top + window.scrollY;
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
      toolbar.show();
    }

    // Hide toolbar
    function hideToolbar(element) {
      if ($(element).is('.editableToolbar')) {
        var toolbar = $(element);
      } else {
        var toolbar = $('.editableToolbar');
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
            toolbar.hide();
          } else {
            $(target).removeClass('hovered');
          }
        }
      }
      toolbar.get(0).I = setTimeout(hide, 50);
    }

    // Makes element editable
    function startEditing(toolbar) {
      toolbar.children().show().end()
        .find('.edit').hide();
      var target = toolbar.get(0).target;
      $(target).attr('contentEditable', true);
      $(target.entity.ui).addClass("active");
      target.focus();
    }

    // Makes element non-editable
    function stopEditing(toolbar) {
      toolbar.children().hide().end()
        .find('.edit').show();
      var target = toolbar.get(0).target;
      $(target).attr('contentEditable', false);
      $(target.entity.ui).removeClass("active");
    }

    if (!$('.editableToolbar').length) {
      // Define toolbar
      var toolbar = $(
        "<div class='editableToolbar'>" +
          "<a href='#' class='edit'></a>" +
          "<a href='#' class='save'></a>" +
          "<a href='#' class='cancel'></a>" +
        "</div>").appendTo($('body'));

      // Attach events            
      toolbar.hover(function () {
        showToolbar(this);
      }, function () {
        this.target.entity.unhover();
      })
      .find('.edit').click(function () {
        startEditing(toolbar);
        return false;
      }).end()
      .find('.save, .cancel').click(function () {
        stopEditing(toolbar);
        return false;
      });
    }

    return this.each(function () {
      // Save value to restore if user presses cancel
      this.prevValue = $(this).html().toString();

      // Show/hide toolbar
      this.showToolbar = function () {
        showToolbar(this);
      }
      this.hideToolbar = function () {
        hideToolbar(this);
      }

      // Hover handler
      $(this).hover(function () {
        this.entity.hover();
      }, function() {
        this.entity.unhover();
      });
    });
  }
})();