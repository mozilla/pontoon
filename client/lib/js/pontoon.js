(function () {

  var Pontoon = {
        app: {
          win: window.top,
          path: ""
        },
        project: {
          win: window,
          url: window.location.href,
          title: window.document.title,
          data: {},
          meta: "",
          page: 0
        },
        locale: {
          code: "",
          language: ""
        },
        user: {
          name: "",
          email: ""
        }
  	  },
      jqueryAppended = false,
      script = document.createElement('script');

  // Main code
  function jqueryLoaded() {
    $(function() {



      /**
       * Send data to main Pontoon code
       */
      function sendData() {
        // Deep copy: http://api.jquery.com/jQuery.extend
        var data = $.extend(true, {}, Pontoon.project.data);
        $(data.pages[Pontoon.project.page].entities).each(function () {
          delete this.node;
        });

        postMessage("data", {
          page: Pontoon.project.page,
          url: Pontoon.project.url,
          title: Pontoon.project.title,
          data: data,
          meta: Pontoon.project.meta
        });
      }



      /**
       * Render main UI and handle events
       */
      function renderHandle() {
        sendData();
        postMessage("render");

        // Update UI and progress when saved
        $(".editableToolbar > .save").click(function () {
          var element = $(this).parent().get(0).target,
              entity = element.entity;

          entity.translation = $($(element).clone()).html();
          sendData();
          postMessage("save", entity.id);
        });

        // Update progress when cancelled
        $(".editableToolbar > .cancel").click(function () {
          var element = $(this).parent().get(0).target,
              entity = element.entity;

          $(element).html(element.prevValue);
          entity.translation = "";
          sendData();
          postMessage("cancel", entity.id);
        });

        // In-place keyboard shortcuts
        $("html").unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
          var key = e.keyCode || e.which,
              toolbar = $(".editableToolbar"),
              save = toolbar.find(".save"),
              target = toolbar.get(0).target,
              entity = target.entity,
              id = entity.id,
              next = id + 1,
              entities = Pontoon.project.data.pages[Pontoon.project.page].entities;

          if (save.is(":visible")) {
            if (key === 13) { // Enter: confirm translation
              save.click();
              target.hideToolbar();
              return false;
            }

            if (key === 27) { // Esc: cancel translation
              toolbar.find(".cancel").click();
              target.hideToolbar();
              return false;
            }

            if (key === 9) { // Tab: confirm + move around entities
              // If on last entity, jump to the first
              if (next > entities.length) {
              	$.each(entities, function() {
                  if (this.body) {
                    next = this.id;
                  }
                });
              }
              save.click();
              $(target).removeClass("hovered");
              postMessage("hover", id);
              entities[next].hover();
              $(".editableToolbar > .edit").click();
              return false;
            }
          }
        });
      }



      /**
       * Extend entity object
       * TODO: move to main.js
       * 
       * e Temporary entity object
       */
      function extendEntity(e) {
        e.hover = function () {
          this.node.get(0).showToolbar();
        };
        e.unhover = function () {
          this.node.get(0).hideToolbar();
        };
      }



      /**
       * Makes DOM nodes editable using contentEditable property
       * Based on editableText plugin by Andris Valums, http://valums.com
       *
       * node DOM node
       */ 
      function makeEditable(node) {
        // Save value to restore if user presses cancel
        node.prevValue = $(node).html().toString();

        // Show/hide toolbar
        node.showToolbar = function () {
          showToolbar(this);
        }
        node.hideToolbar = function () {
          hideToolbar(this);
        }

        // Hover handler
        $(node).hover(function () {
          this.entity.hover();
        }, function() {
          this.entity.unhover();
        });
      }



      /**
       * Extract entities from the document, not prepared for working with Pontoon
       * 
       * Create entity object from every non-empty text node
       * Exclude nodes from special tags, e.g. <script> and <link>
       * Skip nodes already included in parent nodes
       * Add temporary pontoon-entity class to prevent duplicate entities when guessing
       */ 
      function guessEntities() {
        Pontoon.project.data.pages = [{
          title: Pontoon.project.title,
          url: Pontoon.project.url,
          entities: []
        }];
        var counter = 0; // TODO: use IDs or XPath

        // <noscript> contents are not in the DOM
        $('noscript').each(function() {
          $("<div/>", {
          	class: "pontoon-noscript",
            innerHTML: $(this).text()
          }).appendTo("body");
        });

        $(':not("script, style, iframe, noscript")').contents().each(function () {
          if (this.nodeType === Node.TEXT_NODE && $.trim(this.nodeValue).length > 0 && $(this).parents(".pontoon-entity").length === 0) {
            var entity = {};
            entity.id = counter;
            counter++;
            entity.original = $(this).parent().html();

            // Head entities cannot be edited in-place
            if ($(this).parents('head').length === 0) {
              // TODO: remove entity.node from Pontoon.project.data?
              entity.node = $(this).parent(); // HTML Element holding string
              entity.body = true;
              makeEditable(entity.node.get(0)); // Make nodes editable
              entity.node.get(0).entity = entity; // Store entity reference to the node
              extendEntity(entity);
            }

            // Remove entities from child nodes if parent node is entity
            $(this).parent().find(".pontoon-entity").each(function() {
              Pontoon.project.data.pages[Pontoon.project.page].entities.pop(this.entity);
              entity.id--;
              counter--;
            });

            Pontoon.project.data.pages[Pontoon.project.page].entities.push(entity);
            $(this).parent().addClass("pontoon-entity");
          }
        });

        $(".pontoon-entity").removeClass("pontoon-entity");
        $(".pontoon-noscript").remove();
        renderHandle();
      }



      /**
       * Load data from external meta file: original string, translation, comment, suggestions...
       * Match with each string in the document, which is prepended with l10n comment nodes
       * Example: <!--l10n-->Hello World
       *
       * Create entity objects
       * Remove comment nodes
       */
      function loadEntities() {
        var prefix = 'l10n',
            counter = 1, // TODO: use IDs or XPath
            parent = null;

        $.getJSON(Pontoon.project.meta + "/pontoon/" + Pontoon.locale.code + ".json").success(function (data) {
          Pontoon.project.data = data;

          // Find current page entities in metafile
          // TODO: move projects to external domain or folder and use absolute url
          var url = Pontoon.project.win.location.href.split(Pontoon.app.path)[1];
          $(Pontoon.project.data.pages).each(function(i) {
            if (this.url === url) {
              Pontoon.project.page = i;
            }
          });
          var entities = Pontoon.project.data.pages[Pontoon.project.page].entities;

          $('*').contents().each(function () {
            if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf(prefix) === 0) {
              var entity = entities[counter],
                  translation = entity.translation;

              parent = $(this).parent();
              if (translation.length > 0) {
                parent.html(translation);
              } else {
                $(this).remove();
              }

              entity.id = counter;
              // TODO: remove entity.node from Pontoon.project.data?
              entity.node = parent; // HTML Element holding string
              entity.body = true;
              makeEditable(entity.node.get(0)); // Make nodes editable
              entity.node.get(0).entity = entity; // Store entity reference to the node
              extendEntity(entity);
              counter++;
            }
          });
          renderHandle();
        });
      }



      /**
       * Show editable toolbar
       *
       * node DOM node
       */
      function showToolbar(node) {
        if ($(node).is('.editableToolbar')) {
          $(node).get(0).target.entity.hover();
          return true;
        } else {       
          var toolbar = $('.editableToolbar'),
              curTarget = toolbar.get(0).target,
              newTarget = node;
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
        postMessage("hover", newTarget.entity.id);
        toolbar.show();
      }



      /**
       * Hide editable toolbar
       *
       * node DOM node
       */
      function hideToolbar(node) {
        if ($(node).is('.editableToolbar')) {
          var toolbar = $(node);
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
            stopEditing();
            if (target === toolbar.get(0).target) {
              toolbar.get(0).target = null;
              $(target).removeClass('hovered');
              postMessage("unhover", target.entity.id);
              toolbar.hide();
            } else {
              $(target).removeClass('hovered');
              postMessage("unhover", target.entity.id);
            }
          }
        }
        toolbar.get(0).I = setTimeout(hide, 50);
      }



      /**
       * Enable editable mode
       * TODO: remove toolbar parameter and use selector instead
       */
      function startEditing() {
      	var toolbar = $('.editableToolbar');
        toolbar.children().show().end()
          .find('.edit').hide();
        var target = toolbar.get(0).target;
        $(target).attr('contentEditable', true);
        postMessage("active", target.entity.id);
        target.focus();
      }



      /**
       * Disable editable mode
       * TODO: remove toolbar parameter and use selector instead
       */
      function stopEditing() {
      	var toolbar = $('.editableToolbar');
        toolbar.children().hide().end()
          .find('.edit').show();
        var target = toolbar.get(0).target;
        $(target).attr('contentEditable', false);
        postMessage("inactive", target.entity.id);
      }



      /**
       * Handle messages from project code
       */
      function receiveMessage(e) {
        if (e.source === Pontoon.app.win) { // TODO: hardcode Pontoon domain name
          var message = JSON.parse(e.data);
          if (message.type === "hover") {
            Pontoon.project.data.pages[Pontoon.project.page].entities[message.value].hover();
          } else if (message.type === "unhover") {
            Pontoon.project.data.pages[Pontoon.project.page].entities[message.value].unhover();
          } else if (message.type === "edit") {
            $('.editableToolbar > .edit').click();
          } else if (message.type === "save") {
            $('.editableToolbar').get(0).target.entity.node.html(message.value);
            $('.editableToolbar > .save').click();
          } else if (message.type === "cancel") {
            $('.editableToolbar > .cancel').click();
          } else if (message.type === "mode") {
            $("#context .mode").attr("label", message.value + " mode");
          } else if (message.type === "html") {
            $.ajax(Pontoon.project.url).done(function(data) {
              var response = data,
                  index = data.toLowerCase().indexOf("<head"),
                  start = response.substring(0, index);
                  inner = $("html").clone();

              // Remove Pontoon-content
              inner
                .find("script[src*='pontoon.js']").remove().end()
                .find("script[src*='jquery.min.js']").remove().end()
                .find(".editableToolbar").remove().end()
                .find("menu#context").remove();

              postMessage("html", start + inner.html() + "\n</html>");  
            });
          } else if (message.type === "user") {
            Pontoon.user = message.value;
          }
        }
      }

      // Wait for main code messages
      window.addEventListener("message", receiveMessage, false);

      // Inject toolbar stylesheet
      $('<link>', {
        rel: 'stylesheet',
        href: Pontoon.app.path + 'client/lib/css/pontoon.css'
      }).appendTo('head');

      // Prepare editable toolbar
      var toolbar = $(
        "<div class='editableToolbar'>" +
          "<a href='#' class='edit'></a>" +
          "<a href='#' class='save'></a>" +
          "<a href='#' class='cancel'></a>" +
        "</div>").appendTo($('body'));
      toolbar.hover(function () {
        showToolbar(this);
      }, function () {
        hideToolbar(this);
      })
      .find('.edit').click(function () {
        startEditing();
        return false;
      }).end()
      .find('.save, .cancel').click(function () {
        stopEditing();
        return false;
      });

      // Enable context menu
      $('body')
        .attr("contextmenu", "context")
        .append(
        '<menu type="context" id="context">' +
          '<menuitem class="mode" label="Advanced mode" icon="../../client/lib/images/logo-small.png"></menuitem>' +
        '</menu>')
        .find("#context .mode").live("click", function() {
          postMessage("switch");
        });

      // Determine if the current page is prepared for working with Pontoon
      var meta = $('head > meta[name=Pontoon]');
      if (meta.length > 0) {
        if (meta.attr('data-meta')) {
          Pontoon.project.meta = meta.data('meta');
        }
        loadEntities();
      } else {
        // Read meta values
        guessEntities();
      }

    });
  }

  /*
    * window.postMessage improved
    *
    * messageType data type to be sent to the other window
    * messageValue data value to be sent to the other window
    * otherWindow reference to another window
    * targetOrigin specifies what the origin of otherWindow must be
  */
  function postMessage(messageType, messageValue, otherWindow, targetOrigin) {
    var otherWindow = otherWindow || Pontoon.app.win,
        targetOrigin = targetOrigin || "*", // TODO: hardcode Pontoon domain name
        message = {
          type: messageType,
          value: messageValue
        }
    otherWindow.postMessage(JSON.stringify(message), targetOrigin);
  }

  // Load jQuery if not loaded yet
  function loadJquery() {
    if (!window.jQuery) {
      if (!jqueryAppended) {
        script.src = "//ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js";
        document.body.appendChild(script);
        jqueryAppended = true;
        arguments.callee();
      } else {
        window.setTimeout(arguments.callee, 100);
  	  }
    } else {
      jqueryLoaded();
    }
  }

  // Wait for main code trigger
  function initizalize(e) {
    // Prevent execution of any code if page not loaded in Pontoon iframe
    if (e.source === Pontoon.app.win) { // TODO: hardcode Pontoon domain name
      var message = JSON.parse(e.data);
      if (message.type === "locale") {
        Pontoon.locale = message.value.locale; // Set locale
        Pontoon.app.path = message.value.domain; // Set domain
        loadJquery();
        window.removeEventListener("message", initizalize, false);
      }
    }
  }
  window.addEventListener("message", initizalize, false);

  // When loaded inside web client, notify it that project supports Pontoon
  if (window !== window.top) {
    postMessage("supported");
  }

})();
