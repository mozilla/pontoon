(function () {

  // Main code
  function jqueryLoaded() {
    $(function() {



      /**
       * Send data to main Pontoon code
       */
      function sendData() {
        // Deep copy: http://api.jquery.com/jQuery.extend
        var entities = $.extend(true, [], Pontoon.entities);
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

        // Do not change anything when cancelled
        $(".pontoon-editable-toolbar > .cancel").click(function () {
          var element = $(this).parent()[0].target,
              entity = element.entity,
              string = entity.translation[0].string;

          $(element).html(string !== null ? string : entity.original);
          postMessage("INACTIVE", entity.id);
        });

        // In-place keyboard shortcuts
        $("html").unbind("keydown.pontoon").bind("keydown.pontoon", function (e) {
          var key = e.which,
              toolbar = $(".pontoon-editable-toolbar"),
              cancel = toolbar.find(".cancel");

          if (cancel.is(":visible")) {
            if (key === 27) { // Esc: status quo
              cancel.click();
              hideToolbar(toolbar[0].target);
              return false;
            }
          }
        });
      }



      /**
       * Makes DOM nodes hoverable and localizable in the sidebar
       *
       * entity Entity object
       */
      function makeLocalizable(entity) {
        entity.body = true;
        $(entity.node).each(function() {
          this[0].entity = entity; // Store entity reference to the node
 
          this.prop('lang', Pontoon.locale.code);
          this.prop('dir', 'auto');
 
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

        $(':not("script, style, iframe, noscript, [translate=\'no\']")').contents().each(function () {
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

            // Head entities cannot be edited in place
            if ($(this).parents('head').length === 0) {
              entity.node = [parent];
              makeLocalizable(entity);
            }

            // Remove entities from child nodes if parent node is entity
            parent.find(".pontoon-entity").each(function() {
              delete this.entity;
              Pontoon.entities.pop();
              entity.id--;
              counter--;
            });

            Pontoon.entities.push(entity);
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
      function loadEntitiesMatch() {
        var counter = 0,
            elements = {};

        $(':not("script, style, iframe, noscript, [translate=\'no\']")')
          .children().each(function() {
            var text = $.trim($(this).html());
            if (!elements[text]) {
              elements[text] = {
                node: [$(this)],
                body: [!$(this).parents('head').length]
              };
            } else {
              elements[text].node.push($(this));
              elements[text].body.push(!$(this).parents('head').length);
            }
        });

        $(Pontoon.entities).each(function(i, entity) {
          // Renedered text could be different than source
          $('body').append('<div id="pontoon-string">' + entity.original + '</div>');

          var translation = entity.translation[0].string,
              original = $('#pontoon-string').html(),
              element = elements[original];

          entity.id = counter;

          if (element) {
            $(element.node).each(function(i) {
              if (translation !== null) {
                this.html(translation);
              }

              // Head entities cannot be edited in place
              if (element.body[i]) {
                if (!entity.node) {
                  entity.node = [this];
                } else {
                  entity.node.push(this);
                }
                makeLocalizable(entity);
              }
            });
          }

          $('#pontoon-string').remove();
          counter++;
        });

        renderHandle();
      }



      /**
       * Match entities and strings prepended with l10n comment nodes
       * Example: <!--l10n-->Hello World
       */
      function loadEntitiesHooks() {
        var counter = 0,
            l10n = {};

        // Create object with l10n comment nodes
        $(':not("script, style, iframe, noscript, [translate=\'no\']")').contents().each(function () {
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
        $(Pontoon.entities).each(function(i, entity) {
          // Renedered text could be different than source
          $('body').append('<div id="pontoon-string">' + this.original + '</div>');

          var parent = l10n[$('#pontoon-string').html()],
              translation = this.translation[0].string;
          entity.id = counter;

          // Head strings cannot be edited in place
          $(parent).each(function() {
            if (translation !== null) {
              this.html(translation);
            }
            if (this.parents('head').length === 0) {
              if (!entity.node) {
                entity.node = [this];
              } else {
                entity.node.push(this);
              }
              makeLocalizable(entity);
            }
          });

          $('#pontoon-string').remove();
          counter++;
        });

        renderHandle();
      }



      /**
       * Match entities and elements with data-l10n-id attribute
       *
       * TODO: also match HTML attributes
       * https://github.com/l20n/l20n.js
       */
      function loadEntitiesL20n() {
        var counter = 0;

        $(Pontoon.entities).each(function(i, entity) {
          var translation = entity.translation[0].string;
          entity.id = counter;

          $('[data-l10n-id="' + entity.key + '"]').each(function() {
            if (translation !== null) {
              $(this).html(translation);
            }
            if ($(this).parents('head').length === 0 && !$(this).is('input')) {
              if (!entity.node) {
                entity.node = [$(this)];
              } else {
                entity.node.push($(this));
              }
              makeLocalizable(entity);
            }
          });

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

          if ($(curTarget).is('.pontoon-localizing')) {
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
          }
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
          .unbind("dblclick.pontoon").bind("dblclick.pontoon", function() {
            $('.pontoon-editable-toolbar > .edit').click();
          });

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

        if ($(target).is('.pontoon-localizing')) {
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
       * Enable editable mode
       * inplace Was called in place?
       */
      function startEditing(inplace) {
        var toolbar = $('.pontoon-editable-toolbar'),
            target = toolbar[0].target;

        toolbar
          .children().show().end()
          .find('.edit').hide();

        $(target).addClass('pontoon-localizing');
        postMessage("ACTIVE", target.entity.id);
      }



      /**
       * Disable editable mode
       */
      function stopEditing() {
        var toolbar = $('.pontoon-editable-toolbar'),
            target = toolbar[0].target;

        toolbar
          .children().hide().end()
          .find('.edit').show();

        if (!target) {
          return;
        }

        $(target)
          .removeClass('pontoon-localizing')
          .unbind('dblclick.pontoon');
      }



      /**
       * Handle messages from project code
       */
      function receiveMessage(e) {
        if (fromTrustedSource(e)) {
          var message = JSON.parse(e.data);

          switch (message.type) {

          case "HOVER":
            Pontoon.entities[message.value].hover();
            break;

          case "UNHOVER":
            Pontoon.entities[message.value].unhover();
            break;

          case "NAVIGATE":
            // Stop editing old entity
            var target = $('.pontoon-editable-toolbar')[0].target;

            if (target) {
              var entity = target.entity,
                  string = entity.translation[0].string;

              $(target)
                .removeClass('pontoon-localizing')
                .html(string !== null ? string : entity.original);
              hideToolbar(target);
            }

            // Start editing new entity
            var entity = Pontoon.entities[message.value];

            if (entity.body) {
              entity.hover();
              startEditing();
            }
            break;

          case "SAVE":
            var entity = Pontoon.entities[message.value.id],
                translation = message.value.translation;

            entity.translation[0].string = translation;

            $(entity.node).each(function() {
              this.html(translation);
            });
            break;

          case "DELETE":
            if (message.value.id) {
              var entity = Pontoon.entities[message.value.id];

              $(entity.node).each(function() {
                this.html(entity.original);
              });

              entity.translation[0].pk = null;
              entity.translation[0].string = null;
              entity.translation[0].approved = false;
              entity.translation[0].fuzzy = false;
            }
            break;

          case "CANCEL":
            $('.pontoon-editable-toolbar > .cancel').click();
            break;

          case "RESIZE":
            var toolbar = $('.pontoon-editable-toolbar'),
                node = toolbar[0].target;

            if (node) {
              left = node.getBoundingClientRect().left + window.scrollX;
              toolbar.css('left', left);
            }

            break;

          case "UPDATE-ATTRIBUTE":
            var object = message.value.object,
                attribute = message.value.attribute,
                value = message.value.value;

            Pontoon[object][attribute] = value;
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
          "<a href='#' class='cancel'></a>" +
        "</div>").appendTo($('body'));

      toolbar.hover(function () {
        showToolbar(this);
      }, function () {
        hideToolbar(this);
      })
      .find('.edit').click(function () {
        if (toolbar[0].target) {
          startEditing(true);
        }
        return false;
      }).end()
      .find('.cancel').click(function () {
        stopEditing();
        return false;
      });

      $(window).scroll(function(e) {
        var toolbar = $('.pontoon-editable-toolbar'),
            target = toolbar[0].target;

        if (target) {
          var top = target.getBoundingClientRect().top + window.scrollY,

          toolbarTop = top - toolbar.outerHeight();
          toolbar.css('top', toolbarTop);
        }
      });

      // Select appropriate way of loading entities
      var entities = Pontoon.entities;
      if (entities.length > 0) {

        if (entities[0].format === 'ftl') {
          /*
          if (document.l10n) {
            document.l10n.get('main').interactive.then(function() {
              console.log($('[data-l10n-id]').length);
            });
          } else {
            console.log("FAIL");
          }
          */
          var i = 0,
              interval = setInterval(function() {
                if (document.l10n || i > 100) {
                  clearInterval(interval);
                  setTimeout(function() {
                    loadEntitiesL20n();
                  }, 1500);
                } else {
                  i++;
                }
              }, 100);

        } else {
          var hooks = false;

          // Detect hooks
          $(':not("script, style, iframe, noscript, [translate=\'no\']")').contents().filter(function () {
            return this.nodeType == 8;
          }).each(function (i, e) {
            if (e.nodeValue.indexOf('l10n') !== -1) {
              hooks = true;
              return;
            }
          });

          // If available, use hooks to detect translatable nodes
          if (hooks) {
            loadEntitiesHooks();

          // Otherwise match nodes against entities
          } else {
            loadEntitiesMatch();
          }
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
        var script = document.createElement('script');
        script.src = '//pontoon.mozilla.org/static/js/lib/jquery-1.11.1.min.js';
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

  function fromTrustedSource(e) {
    var trustedOrigins = {{ settings.JS_TRUSTED_ORIGINS | to_json() | safe }},
        trusted = trustedOrigins.indexOf(e.origin) > -1;

    if (e.source === appWindow && trusted) {
      return true;
    } else {
      return false;
    }
  }

  // Wait for main code trigger
  function initizalize(e) {
    if (fromTrustedSource(e)) {
      var message = JSON.parse(e.data);
      if (message.type === "ARE YOU READY?") {
        postMessage("READY", null, appWindow, '*');
      }

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
            slug: message.value.slug,
            links: message.value.links
          },
          entities: message.value.entities,
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
        };
    otherWindow.postMessage(JSON.stringify(message), targetOrigin);
  }

  var jqueryAppended = false;
  window.addEventListener("message", initizalize, false);
})();

// When loaded inside web client, notify it and wait for messages
var appWindow = window.opener || ((window !== window.top) ? window.top : undefined);
if (appWindow) {
  appWindow.postMessage(JSON.stringify({
    type: "READY"
  }), '*');
}
