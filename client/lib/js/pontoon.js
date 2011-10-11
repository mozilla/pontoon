(function () {

  var Pontoon = {
        _doc: window,
        _ptn: window.top,
        _locale: "",
        _meta: {},
        _data: {}
  	  },
      jqueryAppended = false,
      script = document.createElement('script');

  // Main code
  function jqueryLoaded() {
    $.noConflict();
    jQuery(document).ready(function($) {

      /**
       * Enable editable text for entities found on the website
       */
      function makeEditable() {
        $(Pontoon._data.entities).each(function () {
          if (this.node) { // 
            this.node.editableText();
          }
        });
      }



      /**
       * Send data to main Pontoon code
       */
      function sendData() {
        // Deep copy: http://api.jquery.com/jQuery.extend
        var data = $.extend(true, {}, Pontoon._data);

        $(data.entities).each(function () {
          delete this.node;
        });
        Pontoon._ptn.postMessage(JSON.stringify(data), "*");

        makeEditable();
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
          this.ui.toggleClass('hovered');
        };
        e.unhover = function () {
          this.node.get(0).hideToolbar();
          this.ui.toggleClass('hovered');
        };
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
        Pontoon._data.entities = [];

        $(':not("script, style")').contents().each(function () {
          if (this.nodeType === Node.TEXT_NODE && $.trim(this.nodeValue).length > 0 && $(this).parents(".pontoon-entity").length === 0) {
            var entity = {};
            entity.original = $(this).parent().html();

            // Head entities cannot be edited in-place
            if ($(this).parents('head').length === 0) {
              entity.node = $(this).parent(); /* HTML Element holding string */
              extendEntity(entity);
            }

            Pontoon._data.entities.push(entity);
            $(this).parent().addClass("pontoon-entity");
          }
        });

        $(".pontoon-entity").removeClass("pontoon-entity");
        sendData();
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
            counter = 1, /* TODO: use IDs or XPath */
            parent = null;

        $.getJSON("pontoon/" + Pontoon._locale + ".json").success(function (data) {
          Pontoon._data = data;
          var entities = Pontoon._data.entities;

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

              entity.node = parent; /* HTML Element holding string */
              extendEntity(entity);
              counter = counter + 1;
            }
          });
          sendData();
        });
      }

      // Inject toolbar stylesheet
      $('<link>', {
        rel: 'stylesheet',
        href: '../../client/lib/css/editable.css'
      }).appendTo('head');

      // Inject editableText jQuery Plugin
      // TODO: jQuerify
      var js = document.createElement('script');
      js.src = "../../client/lib/js/jquery.editableText.js";
      $(js).appendTo('body');

      // Enable context menu
      $('body')
        .attr("contextmenu", "context")
        .append(
        '<menu type="context" id="context">' +
          '<menuitem class="mode" label="Advanced mode" icon="../../client/lib/images/logo-small.png"></menuitem>' +
        '</menu>')
        .find("#context .mode").live("click", function() {
          $("#switch").click();
          if ($("#main").is(".opened")) {
            $(this).attr("label", "Basic mode");
          } else {
            $(this).attr("label", "Advanced mode");
          }
        });

      // Determine if the current page is prepared for working with Pontoon
      // Extract entities from the document
      var meta = $('head > meta[name=Pontoon]');
      if (meta.length > 0) {
        if (meta.attr('content')) {
          Pontoon._meta.project = meta.attr('content');
        }
        if (meta.attr('data-ip')) {
          Pontoon._meta.url = meta.attr('data-ip');
        }
        loadEntities();
      } else {
        // Read meta values
        guessEntities();
      }

    });
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

  // Prevent execution of any code if page not loaded in Pontoon iframe
  function receiveMessage(e) {
    // TODO: hardcode Pontoon domain name in equation with e.origin to check if we trust the sender of this message
    if (e.source === Pontoon._ptn) {
      Pontoon._locale = e.data; // Set locale
      loadJquery();
    }
  }
  window.addEventListener("message", receiveMessage, false);  
  
})();