(function () {

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
          title: Pontoon.project.title
        });

        // Update UI and progress when saved
        $(".pontoon-editable-toolbar > .save").click(function () {
          var element = $(this).parent()[0].target,
              entity = element.entity,
              content = $(element).html();

          if (Pontoon.user.localizer || !entity.translation.approved) {
            entity.translation.string = content;
            $(entity.node).each(function() {
              this.html(content);
            });
            sendData();
          } else {
            $(element).html(entity.translation.string);
          }

          postMessage("UPDATE", {
            id: entity.id,
            content: content
          });
        });

        // Do not change anything when cancelled
        $(".pontoon-editable-toolbar > .cancel").click(function () {
          var element = $(this).parent()[0].target,
              entity = element.entity;

          $(element).html(entity.translation.string || entity.original);
          postMessage("INACTIVE", entity.id);
        });

        // Prevent button click with space
        $("button").unbind("keyup.pontoon").bind("keyup.pontoon", function (e) {
          var key = e.keyCode || e.which;
          if ($(".pontoon-editable-toolbar .save").is(":visible")) {
            if (key === 32) {
              e.preventDefault();
            }
          }
        });

        // In-place keyboard shortcuts
        $("html").unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
          var key = e.keyCode || e.which,
              toolbar = $(".pontoon-editable-toolbar"),
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
              $(target).removeClass('pontoon-hovered');
              postMessage("HOVER", id);
              entities[next].hover();
              $('.pontoon-editable-toolbar > .edit').click();
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



      /*
       * Match entities and elements with exact same contents
       */
      function loadEntitiesLang() {
        var counter = 0;

        $(Pontoon.project.entities).each(function(i, entity) {
          var translation = entity.translation.string,
              original = entity.original;
          entity.id = counter;

          $(':not("script, style, iframe, noscript, [translate=\"no\"]")').children().each(function () {
            if ($(this).html() === original) {
              if (translation) {
                $(this).html(translation);
              }

              // Head entities cannot be edited in-place
              if ($(this).parents('head').length === 0) {
                if (!entity.node) {
                  entity.node = [$(this)];
                } else {
                  entity.node.push($(this));
                }
                makeEditable(entity);
              }
            }
          });

          counter++;
        });

        renderHandle();
      }



      /**
       * Match entities and elements with data-l10n-id attribute
       * https://github.com/fabi1cazenave/webL10n
       */
      function loadEntitiesWebl10n() {
        var counter = 0;

        $(Pontoon.project.entities).each(function(i, entity) {
          var translation = entity.translation.string,
              split = entity.key.split('.'),
              key = split[0],
              attribute = split[1];
          entity.id = counter;

          $('[data-l10n-id="' + key + '"]').each(function() {
            if (translation) {
              if (!attribute) {
                $(this).html(translation);
              } else {
                $(this).attr(attribute, translation);
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
              translation = this.translation.string;
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
        if ($(node).is('.pontoon-editable-toolbar')) {
          showToolbar(node.target);
          return;
        } else {
          var toolbar = $('.pontoon-editable-toolbar'),
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
        $(newTarget)
          .addClass('pontoon-hovered')
          .unbind("dblclick").bind("dblclick", function() {
            $('.pontoon-editable-toolbar > .edit').click();
          })
          // Prevent converting white-spaces at the beginning or
          // in the end of the node to &nbsp; and <br>
          .css('white-space', 'pre-wrap');
        postMessage("HOVER", newTarget.entity.id);
        toolbar.show();
      }



      /**
       * Hide editable toolbar
       *
       * node DOM node
       */
      function hideToolbar(node) {
        if ($(node).is('.pontoon-editable-toolbar')) {
          var toolbar = $(node);
        } else {
          var toolbar = $('.pontoon-editable-toolbar');
        }
        var toolbarNode = toolbar[0],
            target = toolbarNode.target;
        if ($(target).attr('contentEditable') === 'true') {
          return;
        }
        function hide() {
          if (target) {
            target.blur();
            if (target === toolbar[0].target) {
              toolbar[0].target = null;
              $(target).removeClass('pontoon-hovered');
              postMessage("UNHOVER", target.entity.id);
              toolbar.hide();
            } else {
              $(target).removeClass('pontoon-hovered');
              postMessage("UNHOVER", target.entity.id);
            }
          }
        }
        toolbar[0].I = setTimeout(hide, 5);
      }



      /**
       * Select node contents
       *
       * node DOM node
       */
      function selectNodeContents(node) {
        var range = document.createRange();
        range.selectNodeContents(node);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      }



      /**
       * Enable editable mode
       */
      function startEditing() {
        var toolbar = $('.pontoon-editable-toolbar');
        toolbar.children().show().end()
          .find('.edit').hide();
        var target = toolbar[0].target;
        $(target).attr('contentEditable', true);
        postMessage("ACTIVE", target.entity.id);
        selectNodeContents(target);
      }



      /**
       * Disable editable mode
       */
      function stopEditing() {
        var toolbar = $('.pontoon-editable-toolbar');
        toolbar.children().hide().end()
          .find('.edit').show();
        var target = toolbar[0].target;
        if (!target) {
          return;
        }
        $(target).attr('contentEditable', false);
      }



      /**
       * Handle messages from project code
       */
      function receiveMessage(e) {
        if (e.source === Pontoon.app.win) {
          var message = JSON.parse(e.data);

          switch (message.type) {

          case "HOVER":
            Pontoon.project.entities[message.value].hover();
            break;

          case "UNHOVER":
            Pontoon.project.entities[message.value].unhover();
            break;

          case "NAVIGATE":
            // Stop editing old entity
            var target = $('.pontoon-editable-toolbar')[0].target;
            if (target) {
              var entity = target.entity;
              $(target).attr('contentEditable', false);
              $(target).html(entity.translation.string || entity.original);
              hideToolbar(target);
            }
            // Start editing new entity
            var entity = Pontoon.project.entities[message.value];
            if (entity.body) {
              entity.hover();
              startEditing();
            }
            break;

          case "EDIT":
            startEditing();
            break;

          case "SAVE":
            var node = $('.pontoon-editable-toolbar')[0].target.entity.node;
            $(node).each(function() {
              this.html(message.value);
            });
            $('.pontoon-editable-toolbar > .save').click();
            break;

          case "DELETE":
            var target = $('.pontoon-editable-toolbar')[0].target,
                entity = target.entity;
            $(entity.node).each(function() {
              this.html(entity.original);
            });
            selectNodeContents(target);
            entity.translation.approved = false;
            entity.translation.string = '';
            sendData();
            postMessage("DELETE", entity.id);
            break;

          case "CANCEL":
            $('.pontoon-editable-toolbar > .cancel').click();
            break;

          case "MODE":
            $("#context .mode").attr("label", message.value + " mode");
            break;

          case "HTML":
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
                  .find("script[src*='pontoon']").remove().end()
                  .find("script[src*='jquery.min.js']").remove().end()
                  .find(".pontoon-remove").remove().end()
                  .find(".pontoon-editable-toolbar").remove().end()
                  .find("[contenteditable]").removeAttr("contenteditable").end()
                  .find("body").removeAttr("contextmenu").end()
                  .find("menu#context").remove();
                postMessage("HTML", start + inner.html() + "\n</html>");
              }
            });
            break;

          case "RESIZE":
            var toolbar = $('.pontoon-editable-toolbar'),
                node = toolbar[0].target;
            if (node) {
              left = node.getBoundingClientRect().left + window.scrollX;
              toolbar.css('left', left);
            }
            break;

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
        if (!Pontoon.project.links) {
          e.preventDefault();
        }
      });

      // Prepare editable toolbar
      var toolbar = $(
        "<div class='pontoon-editable-toolbar'>" +
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
        toolbar[0].target.focus();
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
          '<menuitem class="mode" label="Advanced mode" icon="' + Pontoon.app.path + 'static/img/logo-small.png' + '"></menuitem>' +
        '</menu>')
        .find("#context .mode").click(function() {
          postMessage("SWITCH");
        });

      // Select appropriate way of loading entities
      var entities = Pontoon.project.entities;
      if (entities.length > 0) {
        if (Pontoon.project.format === 'properties') {
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
        } else if (Pontoon.project.format === 'lang') {
          loadEntitiesLang();
        } else {
          loadEntitiesGettext();
        }
      } else {
        loadEntitiesGuess();
      }
    });
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
    if (e.source === appWindow) {
      var message = JSON.parse(e.data);
      if (message.type === "INITIALIZE") {
        Pontoon = {
          app: {
            win: appWindow,
            path: message.value.path,
          },
          project: {
            win: window,
            url: window.location.href,
            title: document.title.split("-->")[1] || document.title,
            entities: message.value.entities,
            pk: message.value.pk,
            format: message.value.format,
            links: message.value.links
          },
          locale: message.value.locale,
          user: message.value.user
        };

        loadJquery();
        window.removeEventListener("message", initizalize, false);
      }
    }
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
    var otherWindow = otherWindow || appWindow,
        targetOrigin = targetOrigin || Pontoon.app.path,
        message = {
          type: messageType,
          value: messageValue
        }
    otherWindow.postMessage(JSON.stringify(message), targetOrigin);
  }

  var appWindow = window.opener || ((window !== window.top) ? window.top : undefined),
      jqueryAppended = false,
      script = document.createElement('script');

  // When loaded inside web client, notify it that project supports Pontoon
  if (window.opener || (window !== window.top)) {
    postMessage("READY", null, null, "*");
  }

  window.addEventListener("message", initizalize, false);
})();
