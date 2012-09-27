(function () {

  var Pontoon = {
        app: {
          win: window.opener || window.top,
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
          var element = $(this).parent().get(0).target,
              entity = element.entity;

          entity.translation = (entity.node.html() !== entity.original) ? $($(element).clone()).html() : '';
          sendData();
          postMessage("UPDATE", entity.id);
        });

        // Do not change anything when cancelled
        $(".editableToolbar > .cancel").click(function () {
          var element = $(this).parent().get(0).target,
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
            var target = toolbar.get(0).target,
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
              return false;
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
        var node = entity.node.get(0);
        entity.body = true;
        node.entity = entity; // Store entity reference to the node
        
        // Show/hide toolbar on entity hover
        entity.hover = function () {
          showToolbar(this.node.get(0));
        };
        entity.unhover = function () {
          hideToolbar(this.node.get(0));
        };

        // Show/hide toolbar on node hover
        $(node).hover(function () {
          showToolbar(this);
        }, function() {
          hideToolbar(this);
        });
      }



      /**
       * Extract entities from webL10n apps
       * https://github.com/fabi1cazenave/webL10n
       */
      function webL10nEntities(data) {
        var counter = 0;

        $('[data-l10n-id]').each(function () {
          var entity = {},
              parent = $(this);

          // Match strings in the document with DB data
          $(data).each(function() {
            if (this.key === parent.attr('data-l10n-id')) {
              entity.id = counter;
              counter++;
              entity.original = this.original;
              var translation = this.translation;
              if (translation.length > 0) {
                entity.translation = translation;
                if (!parent.attr('placeholder')) {
                  parent.html(translation);
                } else {
                  parent.attr('placeholder', translation);
                }
              }
              this.pontoon = true;

              // Head entities and input box placeholders cannot be edited in-place
              if (parent.parents('head').length === 0 && !parent.is('input')) {
                entity.node = parent;
                makeEditable(entity);
              }

              Pontoon.project.entities.push(entity);
            }
          });
        });

        // Prepare unmatched DB entities to be displayed in Advanced mode
        $(data).each(function() {
          if(!this.pontoon) {
            var entity = {};
            entity.id = counter;
            counter++;
            entity.original = this.original;
            var translation = this.translation;
            if (translation.length > 0) {
              entity.translation = translation;
            }
            Pontoon.project.entities.push(entity);
          }
        });

        Pontoon.project.type = 'webL10n'
        renderHandle();
      }



      /**
       * Extract entities from the document, not prepared for working with Pontoon
       * 
       * Create entity object from every non-empty text node
       * Exclude nodes from special tags (e.g. <script>) and with translate=no attribute
       * Skip nodes already included in parent nodes
       * Add temporary pontoon-entity class to prevent duplicate entities when guessing
       */ 
      function guessEntities() {
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
              entity.node = parent;
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
       * Load data from DB: original string, translation, comment, suggestions...
       * Match with each string in the document, which is prepended with l10n comment nodes
       * Example: <!--l10n-->Hello World
       *
       * Create entity objects
       * Remove comment nodes
       */
      function loadEntities() {
        var counter = 0,
            params = {
              locale: Pontoon.locale.code,
              url: Pontoon.project.url
            };

        $.ajax({
          url: Pontoon.app.path + 'load/',
          data: params,
          dataType: 'jsonp',
          error: function(data) {
            postMessage("ERROR");
            $('menu#context').remove();
          },
          success: function(data) {
            if (data === "error") {
              postMessage("ERROR");
              $('menu#context').remove();
              return;
            } else if (data === "guess") {
              guessEntities();
              return;
            } else if (data[0].key) {
              webL10nEntities(data);
              return;
            }
            $('*').contents().each(function () {
              if (this.nodeType === Node.COMMENT_NODE && this.nodeValue.indexOf('l10n') === 0) {
                var entity = {},
                    parent = $(this).parent();
                $(this).remove();

                // Match strings in the document with DB data
                $(data).each(function() {
                  // Renedered text could be different than source
                  parent.after('<div id="pontoon-string" style="display: none">' + this.original + '</div>');

                  if ($('#pontoon-string').html() === parent.html()) {
                    entity.id = counter;
                    entity.original = this.original;
                    entity.comment = this.comment;
                    var translation = this.translation;
                    if (translation.length > 0) {
                      entity.translation = translation;
                      parent.html(translation);
                    }

                    // Head strings cannot be edited in-place
                    if ($(this).parents('head').length === 0) {
                      entity.node = parent;
                      makeEditable(entity);
                    }

                    // Do not save if duplicate
                    if (!this.pontoon) {
                      Pontoon.project.entities.push(entity);
                      counter++;
                      this.pontoon = true;
                    }
                  }
                  $('#pontoon-string').remove();
                });
              }
            });

            // Prepare unmatched DB entities to be displayed in Advanced mode
            $(data).each(function() {
              if(!this.pontoon) {
                var entity = {};
                entity.id = counter;
                counter++;
                entity.original = this.original;
                entity.comment = this.comment;
                var translation = this.translation;
                if (translation.length > 0) {
                  entity.translation = translation;
                }
                Pontoon.project.entities.push(entity);
              }
            });

            renderHandle();
          }
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
        var toolbarNode = toolbar.get(0);
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
              postMessage("UNHOVER", target.entity.id);
              toolbar.hide();
            } else {
              $(target).removeClass('hovered');
              postMessage("UNHOVER", target.entity.id);
            }
          }
        }
        toolbar.get(0).I = setTimeout(hide, 50);
      }



      /**
       * Enable editable mode
       */
      function startEditing() {
        var toolbar = $('.editableToolbar');
        toolbar.children().show().end()
          .find('.edit').hide();
        var target = toolbar.get(0).target;
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
        var target = toolbar.get(0).target;
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
            $('.editableToolbar').get(0).target.entity.node.html(message.value);
            $('.editableToolbar > .save').click();
          } else if (message.type === "DELETE") {
            var entity = $('.editableToolbar').get(0).target.entity;
            entity.node.html(entity.original);
            entity.translation = '';
            sendData();
            postMessage("UPDATE", entity.id);
            $('.editableToolbar > .cancel').click();
          } else if (message.type === "CANCEL") {
            $('.editableToolbar > .cancel').click();
          } else if (message.type === "MODE") {
            $("#context .mode").attr("label", message.value + " mode");
          } else if (message.type === "HTML") {
            $.ajax(Pontoon.project.url).done(function(data) {
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
      loadEntities();
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
