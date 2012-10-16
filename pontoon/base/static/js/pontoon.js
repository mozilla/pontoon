(function () {

  var Pontoon = {
        app: {
          win: window.opener || ((window !== window.top) ? window.top : undefined),
          path: "",
          external: false,
          links: false
       },
        project: {
          win: window,
          url: window.location.href,
          title: "",
          entities: [],
          pk: null,
          type: 'gettext'
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
        var entities = $.extend(true, [], Pontoon.project.entities);
        $(entities).each(function () {
          delete this.node;
        });

        postMessage("DATA", {
          entities: entities
        });
      }



      /**
       * Render main UI and handle events
       */
      function renderHandle() {
        sendData();
        postMessage("RENDER", {
          url: Pontoon.project.url,
          title: Pontoon.project.title,
          type: Pontoon.project.type
        });

        // Update UI and progress when saved
        $(".editableToolbar > .save").click(function () {
          var element = $(this).parent()[0].target,
              entity = element.entity,
              content = $(element).html();

          entity.translation = content;
          $(entity.node).each(function() {
            this.html(content);
          });
          sendData();
          postMessage("UPDATE", entity.master || entity.id);
        });

        // Do not change anything when cancelled
        $(".editableToolbar > .cancel").click(function () {
          var element = $(this).parent()[0].target,
              entity = element.entity;

          $(element).html(entity.translation || entity.original);
        });

        // In-place keyboard shortcuts
        $("html").unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
          var key = e.keyCode || e.which,
              toolbar = $(".editableToolbar"),
              save = toolbar.find(".save"),
              cancel = toolbar.find(".cancel");

          if (save.is(":visible")) {
            var target = toolbar[0].target,
                entity = target.entity,
                id = entity.id,
                next = id + 1,
                entities = Pontoon.project.entities;

            if (key === 13) { // Enter: confirm translation
              save.click();
              hideToolbar(target);
              return false;
            }

            if (key === 27) { // Esc: status quo
              cancel.click();
              hideToolbar(target);
              return false;
            }

            if (key === 9) { // Tab: status quo + move around entities
              // Disabled.
              // TODO: re-number entities and re-enable
              return false;
              // If on last entity, jump to the first
              if (next > entities.length) {
                $.each(entities, function() {
                  if (this.body) {
                    next = this.id;
                  }
                });
              }
              cancel.click();
              $(target).removeClass("hovered");
              postMessage("HOVER", id);
              entities[next].hover();
              $(".editableToolbar > .edit").click();
            }
          }
        });
      }



      /**
       * Makes DOM nodes editable using contentEditable property
       *
       * entity Entity object
       */ 
      function makeEditable(entity) {
        entity.body = true;
        $(entity.node).each(function() {
          this[0].entity = entity; // Store entity reference to the node

          // Show/hide toolbar on node hover
          if (!this.handlersAttached) {
            this.hover(function () {
              showToolbar(this);
            }, function() {
              hideToolbar(this);
            });
            this.handlersAttached = true;
          }
        });

        // Show/hide toolbar on entity hover
        entity.hover = function () {
          showToolbar(this.node[0][0]);
        };
        entity.unhover = function () {
          hideToolbar(this.node[0][0]);
        };
      }



      /**
       * Extract entities from the document, not prepared for working with Pontoon
       *
       * Create entity object from every non-empty text node
       * Exclude nodes from special tags (e.g. <script>) and with translate=no attribute
       * Skip nodes already included in parent nodes
       * Add temporary pontoon-entity class to prevent duplicate entities when guessing
       */
      function loadEntitiesGuess() {
        var counter = 0;

        // <noscript> contents are not in the DOM
        $('noscript').each(function() {
          $("<div/>", {
            class: "pontoon-noscript",
            innerHTML: $(this).text()
          }).appendTo("body");
        });

        $(':not("script, style, iframe, noscript, [translate=\"no\"]")').contents().each(function () {
          if (this.nodeType === Node.TEXT_NODE && $.trim(this.nodeValue).length > 0 && $(this).parents(".pontoon-entity").length === 0) {
            var entity = {},
                parent = $(this).parent();

            // If project uses hooks, but not available in the DB, remove <!--l10n--> comment nodes
            parent.contents().each(function () {
              if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf('l10n') === 0) {
                $(this).remove();
              }
            });

            entity.id = counter;
            counter++;
            entity.original = parent.html();

            // Head entities cannot be edited in-place
            if ($(this).parents('head').length === 0) {
              entity.node = [parent];
              makeEditable(entity);
            }

            // Remove entities from child nodes if parent node is entity
            parent.find(".pontoon-entity").each(function() {
              delete this.entity;
              Pontoon.project.entities.pop();
              entity.id--;
              counter--;
            });

            Pontoon.project.entities.push(entity);
            parent.addClass("pontoon-entity");
          }
        });

        $(".pontoon-entity").removeClass("pontoon-entity");
        $(".pontoon-noscript").remove();
        renderHandle();
      }



      /**
       * Match entities and elements with data-l10n-id attribute
       * https://github.com/fabi1cazenave/webL10n
       */
      function loadEntitiesWebl10n() {
        var counter = 0;

        $(Pontoon.project.entities).each(function(i, entity) {
          var translation = entity.translation;
          entity.id = counter;

          $('[data-l10n-id="' + entity.key + '"]').each(function() {
            if (translation) {
              if (!$(this).attr('placeholder')) {
                $(this).html(translation);
              } else {
                $(this).attr('placeholder', translation);
              }
            }
            if ($(this).parents('head').length === 0 && !$(this).is('input')) {
              if (!entity.node) {
                entity.node = [$(this)];
              } else {
                entity.node.push($(this));
              }
              makeEditable(entity);
            }
          });

          counter++;
        });

        renderHandle();
      }



      /**
       * Match entities and strings prepended with l10n comment nodes
       * Example: <!--l10n-->Hello World
       */
      function loadEntitiesGettext() {
        var counter = 0,
            l10n = {};

        // Create object with l10n comment nodes
        $('*').contents().each(function () {
          if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf('l10n') === 0) {
            var element = $(this).parent();
            $(this).remove();
            if (!l10n[element.html()]) {
              l10n[element.html()] = [element];
            } else {
              l10n[element.html()].push(element);
            }
          }
        });

        // Match l10n comment nodes with DB data
        $(Pontoon.project.entities).each(function(i, entity) {
          // Renedered text could be different than source
          $('body').append('<div id="pontoon-string" style="display: none">' + this.original + '</div>');

          var parent = l10n[$('#pontoon-string').html()],
              translation = this.translation;
          entity.id = counter;

          // Head strings cannot be edited in-place
          $(parent).each(function() {
            if (translation) {
              this.html(translation);
            }
            if (this.parents('head').length === 0) {
              if (!entity.node) {
                entity.node = [this];
              } else {
                entity.node.push(this);
              }
              makeEditable(entity);
            }
          });

          $('#pontoon-string').remove();
          counter++;
        });

        renderHandle();
      }



      /**
       * Show editable toolbar
       *
       * node DOM node
       */
      function showToolbar(node) {
        if ($(node).is('.editableToolbar')) {
          showToolbar(node.target);
          return;
        } else {
          var toolbar = $('.editableToolbar'),
              curTarget = toolbar[0].target,
              newTarget = node;
          if ($(curTarget).attr('contentEditable') === 'true') {
            return;
          }
          if (curTarget && curTarget !== newTarget) {
            hideToolbar(curTarget);
          }

          // Toolbar position
          var left = newTarget.getBoundingClientRect().left + window.scrollX,
              top = newTarget.getBoundingClientRect().top + window.scrollY,
              toolbarTop = top - toolbar.outerHeight();

          toolbar.css('left', left);
          // Display toolbar at the bottom if otherwise too high
          if (toolbarTop >= 0) {
            toolbar.removeClass('bottom').css('top', toolbarTop);
          } else{
            toolbar.addClass('bottom').css('top', top + $(newTarget).outerHeight());
          };
        }

        var toolbarNode = toolbar[0];
        if (toolbarNode.I !== null) {
          clearTimeout(toolbarNode.I);
          toolbarNode.I = null;
        }
        if (newTarget) {
          toolbarNode.target = newTarget;
        }
        $(newTarget).addClass('hovered');
        postMessage("HOVER", newTarget.entity.id);
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
        var toolbarNode = toolbar[0],
            target = toolbarNode.target;
        if ($(target).attr('contentEditable') === 'true') {
          return;
        }
        function hide() {
          if (target) {
            target.blur();
            stopEditing();
            if (target === toolbar[0].target) {
              toolbar[0].target = null;
              $(target).removeClass('hovered');
              postMessage("UNHOVER", target.entity.id);
              toolbar.hide();
            } else {
              $(target).removeClass('hovered');
              postMessage("UNHOVER", target.entity.id);
            }
          }
        }
        toolbar[0].I = setTimeout(hide, 50);
      }



      /**
       * Enable editable mode
       */
      function startEditing() {
        var toolbar = $('.editableToolbar');
        toolbar.children().show().end()
          .find('.edit').hide();
        var target = toolbar[0].target;
        $(target).attr('contentEditable', true);
        postMessage("ACTIVE", target.entity.id);
        target.focus();
      }



      /**
       * Disable editable mode
       */
      function stopEditing() {
        var toolbar = $('.editableToolbar');
        toolbar.children().hide().end()
          .find('.edit').show();
        var target = toolbar[0].target;
        if (!target) {
          return;
        }
        $(target).attr('contentEditable', false);
        postMessage("INACTIVE", target.entity.id);
      }



      /**
       * Handle messages from project code
       */
      function receiveMessage(e) {
        if (e.source === Pontoon.app.win) { // TODO: hardcode Pontoon domain name
          var message = JSON.parse(e.data);
          if (message.type === "HOVER") {
            Pontoon.project.entities[message.value].hover();
          } else if (message.type === "UNHOVER") {
            Pontoon.project.entities[message.value].unhover();
          } else if (message.type === "EDIT") {
            $('.editableToolbar > .edit').click();
          } else if (message.type === "SAVE") {
            $($('.editableToolbar')[0].target.entity.node).each(function() {
              this.html(message.value);
            });
            $('.editableToolbar > .save').click();
          } else if (message.type === "DELETE") {
            var entity = $('.editableToolbar')[0].target.entity;
            $(entity.node).each(function() {
              this.html(entity.original);
            });
            entity.translation = '';
            sendData();
            postMessage("UPDATE", entity.id);
            $('.editableToolbar > .cancel').click();
          } else if (message.type === "CANCEL") {
            $('.editableToolbar > .cancel').click();
          } else if (message.type === "MODE") {
            $("#context .mode").attr("label", message.value + " mode");
          } else if (message.type === "HTML") {
            $.ajax({
              url: Pontoon.project.url,
              success: function(data) {
                var response = data,
                    index = data.toLowerCase().indexOf("<head"),
                    start = response.substring(0, index);
                    inner = $("html").clone();
                // Remove Pontoon-content
                inner
                  .find("link[href*='pontoon.css']").remove().end()
                  .find("script[src*='pontoon.js']").remove().end()
                  .find("script[src*='jquery.min.js']").remove().end()
                  .find(".editableToolbar").remove().end()
                  .find("[contenteditable]").removeAttr("contenteditable").end()
                  .find("body").removeAttr("contextmenu").end()
                  .find("menu#context").remove();
                postMessage("HTML", start + inner.html() + "\n</html>");
              }
            });
          } else if (message.type === "USER") {
            Pontoon.user = message.value;
          }
        }
      }

      // Wait for main code messages
      window.addEventListener("message", receiveMessage, false);

      // Inject toolbar stylesheet
      $('<link>', {
        rel: 'stylesheet',
        href: Pontoon.app.path + 'static/css/pontoon.css'
      }).appendTo('head');

      // Disable links
      $('a').click(function(e) {
        if (!Pontoon.app.links) {
          e.preventDefault();
        }
      });

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
      if (!Pontoon.app.external) {
        $('body')
          .attr("contextmenu", "context")
          .append(
          '<menu type="context" id="context">' +
            '<menuitem class="mode" label="Advanced mode" icon="' + Pontoon.app.path + 'static/img/logo-small.png' + '"></menuitem>' +
          '</menu>')
          .find("#context .mode").live("click", function() {
            postMessage("SWITCH");
          });
      }

      Pontoon.project.title = document.title.split("-->")[1] || document.title;        

      // Select appropriate way of loading entities
      var entities = Pontoon.project.entities;
      if (entities.length > 0) {
        if (entities[0].key) {
          var localized = false;
          window.addEventListener("localized", function() {
            if (!localized && document.webL10n.getReadyState() === 'complete') {
              localized = true;
              loadEntitiesWebl10n();
            }
          }, false);
          // Fallback: some apps don't seem to trigger the event
          setTimeout(function() {
            if (!localized) {
              loadEntitiesWebl10n();
            }
          }, 1000);
          Pontoon.project.type = 'webL10n';
        } else {
          loadEntitiesGettext();
        }
      } else {
        loadEntitiesGuess();
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
      if (!jqueryAppended && document.body) {
        script.src = Pontoon.app.path + 'static/js/jquery-1.7.2.min.js';
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
      if (message.type === "INITIALIZE") {
        Pontoon.locale = message.value.locale; // Set locale
        Pontoon.app.path = message.value.path; // Set domain
        Pontoon.app.external = message.value.external; // Set external
        Pontoon.app.links = message.value.links; // Set links
        Pontoon.project.entities = message.value.entities; // Set entities
        Pontoon.project.pk = message.value.pk; // Set project
        loadJquery();
        window.removeEventListener("message", initizalize, false);
      }
    }
  }
  window.addEventListener("message", initizalize, false);

  // When loaded inside web client, notify it that project supports Pontoon
  if (window.opener || (window !== window.top)) {
    postMessage("SUPPORTED");
  }

})();
