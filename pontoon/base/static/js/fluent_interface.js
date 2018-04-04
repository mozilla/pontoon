/* global FluentSyntax */
var fluentParser = new FluentSyntax.FluentParser({ withSpans: false });
var fluentSerializer = new FluentSyntax.FluentSerializer();

/* Public functions used across different files */
var Pontoon = (function (my) {

  /*
   * Is ast element of type that can be presented as a simple string:
   * - TextElement
   * - Placeable with expression type CallExpression, ExternalArgument
   *   or MessageReference
   */
  function isSimpleElement(element) {
    if (element.type === 'TextElement') {
      return true;
    }

    // Placeable
    if (
      element.expression &&
      [
        'CallExpression',
        'ExternalArgument',
        'MessageReference'
      ].indexOf(element.expression.type) >= 0
    ) {
      return true;
    }

    return false;
  }

  /*
   * Is ast element representing a pluralized string?
   *
   * Keys of all variants of such elements are either
   * CLDR plurals or numbers.
   */
  function isPluralElement(element) {
    if (!(element.expression && element.expression.type === 'SelectExpression')) {
      return false;
    }

    var CLDRplurals = ['zero', 'one', 'two', 'few', 'many', 'other'];

    return element.expression.variants.every(function (item) {
      return (
        CLDRplurals.indexOf(item.key.name) !== -1 ||
        item.key.type === 'NumberExpression'
      );
    });
  }

  /*
   * Are all elements supported in rich FTL editor?
   *
   * Elements are supported if they are:
   * - simple elements or
   * - select expressions
   */
  function areSupportedElements(elements) {
    return elements.every(function(element) {
      return (
        isSimpleElement(element) ||
        (element.expression && element.expression.type === 'SelectExpression')
      );
    });
  }

  /*
   * Is ast of a message, supported in rich FTL editor?
   *
   * Message is supported if it's valid and all value elements
   * and all attribute elements are supported.
   */
  function isSupportedMessage(ast) {
    // Parse error
    if (ast.type === 'Junk') {
      return false;
    }

    var valueSupported = !ast.value || areSupportedElements(ast.value.elements);
    var attributesSupported = ast.attributes.every(function (attribute) {
      return attribute.value && areSupportedElements(attribute.value.elements);
    });

    return valueSupported && attributesSupported;
  }

  /*
   * Is ast of a simple message?
   *
   * A simple message has no attributes and all value
   * elements are simple.
   */
  function isSimpleMessage(ast) {
    if (
      ast &&
      !ast.attributes.length &&
      ast.value &&
      ast.value.elements.every(function(item) {
        return isSimpleElement(item);
      })
    ) {
      return true;
    }

    return false;
  }

  /*
   * Render textarea element with the given properties
   */
  function renderTextareaElement(id, value, maxlength) {
    var element = '<textarea class="value" id="ftl-id-' + id + '"';

    if (typeof maxlength !== 'undefined' && maxlength !== null) {
      element += ' maxlength="' + maxlength + '"';
    }

    element += ' dir="' + Pontoon.locale.direction +
      '" data-script="' + Pontoon.locale.script +
      '" lang="' + Pontoon.locale.code + '">' + value + '</textarea>';
    return element;
  }

  /*
   * Render original string element with given title and ast elements
   */
  function renderOriginalElement(title, elements) {
    return '<li>' +
      '<span class="id">' +
        title +
      '</span>' +
      '<span class="value">' +
        stringifyElements(elements, true) +
      '</span>' +
    '</li>';
  }

  /*
   * Render editor element with given title and ast elements
   */
  function renderEditorElement(title, elements, isPlural, isTranslated) {
    // Special case: Access keys
    var maxlength = '';
    var accesskeysDiv = '';
    if (title === 'accesskey') {
      maxlength = '1';
      accesskeysDiv = '<div class="accesskeys"></div>';
    }

    // Special case: Plurals
    var exampleSpan = '';
    if (isPlural) {
      var example = Pontoon.locale.plural_examples[title];

      if (example !== undefined) {
        exampleSpan = '<span> (e.g. ' +
          '<span class="stress">' + example + '</span>' +
        ')</span>';
      }
    }

    var value = isTranslated ? stringifyElements(elements) : '';
    var textarea = renderTextareaElement(title, value, maxlength);

    return '<li>' +
      '<label class="id" for="ftl-id-' + title + '">' +
        '<span>' + title + '</span>' +
        exampleSpan +
      '</label>' +
      accesskeysDiv +
      textarea +
    '</li>';
  }

  /*
   * Render original string elements
   *
   * - Adjoining simple elements are concatenated and presented as a simple string
   * - SelectExpression elements are presented as a list of variants
   */
  function renderOriginalElements(elements, title) {
    var content = '';
    var simpleElements = [];

    elements.forEach(function (element, i) {
      var isLastElement = i === elements.length - 1;

      // Collect simple elements
      if (isSimpleElement(element)) {
        simpleElements.push(element);
      }

      // Render collected simple elements when non-simple or last element is met
      if ((!isSimpleElement(element) || isLastElement) && simpleElements.length) {
        content += renderOriginalElement(title, simpleElements);
        simpleElements = [];
      }

      // Render SelectExpression
      if (element.expression && element.expression.type === 'SelectExpression') {
        element.expression.variants.forEach(function (item) {
          content += renderOriginalElement(item.key.value || item.key.name, item.value.elements);
        });
      }
    });

    return content;
  }

  /*
   * Render editor elements
   *
   * - Adjoining simple elements are concatenated and presented as a simple string
   * - SelectExpression elements are presented as a list of variants
   */
  function renderEditorElements(elements, title, isTranslated) {
    var content = '';
    var simpleElements = [];

    elements.forEach(function (element, i) {
      var isLastElement = i === elements.length - 1;

      // Collect simple elements
      if (isSimpleElement(element)) {
        simpleElements.push(element);
      }

      // Render collected simple elements when non-simple or last element is met
      if ((!isSimpleElement(element) || isLastElement) && simpleElements.length) {
        content += renderEditorElement(title, simpleElements, false, isTranslated);
        simpleElements = [];
      }

      // Render SelectExpression
      if (element.expression && element.expression.type === 'SelectExpression') {
        var expression = fluentSerializer.serializeExpression(element.expression.expression);
        content += '<li data-expression="' + expression + '"><ul>';

        if (isPluralElement(element) && !isTranslated) {
          Pontoon.locale.cldr_plurals.forEach(function (pluralName) {
            content += renderEditorElement(pluralName, [], true, isTranslated);
          });
        }
        else {
          element.expression.variants.forEach(function (item) {
            content += renderEditorElement(
              item.key.value || item.key.name,
              item.value.elements,
              isPluralElement(element),
              isTranslated
            );
          });
        }

        content += '</ul></li>';
      }
    });

    return content;
  }

  /*
   * Serialize values in FTL editor forms into an FTL string
   *
   * elementNodes A set of jQuery nodes
   */
  function serializeFTLEditorElements(elementNodes) {
    var value = '';

    elementNodes.each(function (i, node) {
      var expression = $(node).data('expression');

      // Simple element
      if (!expression) {
        value += $(this).find('textarea').val();
      }

      // SelectExpression
      else {
        var nodeValue = expression + ' ->';
        var variants = $(node).find('ul li');
        var hasTranslatedVariants = false;
        var defaultMarker = '';

        variants.each(function(index) {
          var id = $(this).find('.id span:first').html();
          var val = $(this).find('.value').val();

          // TODO: UI should allow for explicitly selecting a default variant
          if (index === variants.length - 1) {
            defaultMarker = '*';
          }

          if (id && val) {
            nodeValue += '\n  ' + defaultMarker + '[' + id + '] ' + val;
            hasTranslatedVariants = true;
          }
        });

        if (hasTranslatedVariants) {
          value += '{ ' + nodeValue + '\n  }';
        }
      }
    });

    return value;
  }

  /*
   * Convert AST elements of type TextElement or Placeable to string
   *
   * elements AST elements
   * markPlaceables Should placeables be marked up?
   */
  function stringifyElements(elements, markPlaceables) {
    var string = '';
    var startMarker = '';
    var endMarker = '';

    elements.forEach(function (element) {
      if (element.type === 'TextElement') {
        if (markPlaceables) {
          string += Pontoon.markXMLTags(element.value);
        }
        else {
          string += element.value;
        }
      }
      else if (element.type === 'Placeable') {
        if (element.expression.type === 'ExternalArgument') {
          if (markPlaceables) {
            startMarker = '<mark class="placeable" title="External Argument">';
            endMarker = '</mark>';
          }
          string += startMarker + '{$' + element.expression.id.name + '}' + endMarker;
        }
        else if (element.expression.type === 'MessageReference') {
          if (markPlaceables) {
            startMarker = '<mark class="placeable" title="Message Reference">';
            endMarker = '</mark>';
          }
          string += startMarker + '{' + element.expression.id.name + '}' + endMarker;
        }
        else if (element.expression.type === 'CallExpression') {
          if (markPlaceables) {
            startMarker = '<mark class="placeable" title="Call Expression">';
            endMarker = '</mark>';
          }
          var expression = fluentSerializer.serializeExpression(element.expression);
          string += startMarker + '{' + expression + '}' + endMarker;
        }
        else if (element.expression.type === 'SelectExpression') {
          var variantElements = element.expression.variants.filter(function (variant) {
            return variant.default;
          })[0].value.elements;
          string += stringifyElements(variantElements);
        }
      }
    });

    return string;
  }

  /*
   * Perform error checks for provided translationAST and entityAST
   */
  function runChecks(translationAST, entityAST) {
    // Parse error
    if (translationAST.type === 'Junk') {
      return translationAST.annotations[0].message;
    }

    // TODO: Should be removed by bug 1237667
    // Detect missing values
    else if (entityAST.value && !translationAST.value) {
      return 'Please make sure to fill in the value';
    }

    // Detect missing attributes
    else if (
      entityAST.attributes &&
      translationAST.attributes &&
      entityAST.attributes.length !== translationAST.attributes.length
    ) {
      return 'Please make sure to fill in all the attributes';
    }

    // Detect Message ID mismatch
    else if (entityAST.id.name !== translationAST.id.name) {
      return 'Please make sure the translation key matches the source string key';
    }
  }

  /*
   * Toggle translation length and Copy button in editor toolbar
   */
  function toggleEditorToolbar() {
    var entity = Pontoon.getEditorEntity();
    var show = entity.format !== 'ftl' || !Pontoon.fluent.isComplexFTL();

    $('#translation-length, #copy').toggle(show);

    if ($('#translation-length').is(':visible')) {
      var original = Pontoon.fluent.getSimplePreview(entity, entity.original, entity);
      $('#translation-length').find('.original-length').html(original.length);
    }
  }

  return $.extend(true, my, {
    fluent: {

      /*
       * Is FTL editor enabled?
       */
      isFTLEditorEnabled: function () {
        return $('#ftl-area').is(':visible');
      },


      /*
       * Is Source FTL editor enabled?
       */
      isSourceFTLEditorEnabled: function () {
        return $('#ftl:visible').is('.active');
      },


      /*
       * Is string in FTL editor complex?
       * As opposed to simple which only contains a string value.
       */
      isComplexFTL: function () {
        return !$('#only-value').is(':visible');
      },


      /*
       * Toggle FTL button visibility
       */
      toggleButton: function () {
        var entity = Pontoon.getEditorEntity();
        $('#ftl').toggle(entity.format === 'ftl');
      },


      /*
       * Toggle between source and FTL translation editor
       */
      toggleEditor: function (showFTL) {
        var entity = Pontoon.getEditorEntity();
        if (typeof showFTL === 'undefined' || showFTL === null) {
          showFTL = entity.format === 'ftl';
        }

        if (showFTL) {
          $('#ftl-area').show();
          $('#translation').hide();
          $('#ftl').removeClass('active');
        }
        else {
          $('#ftl-area').hide();
          $('#translation').show().focus();
          $('#ftl').addClass('active');
        }

        toggleEditorToolbar();
        Pontoon.moveCursorToBeginning();
      },


      /*
       * Get source string value of a simple FTL message to be used in
       * tje Copy (original to translation) function
       */
      getSourceStringValue: function (entity, fallback) {
        if (entity.format !== 'ftl' || this.isComplexFTL()) {
          return fallback;
        }

        var ast = fluentParser.parseEntry(entity.original);
        return stringifyElements(ast.value.elements);
      },


      /*
       * Return translation in the editor as FTL source to be used
       * in unsaved changes check. If translation contains errors,
       * return error message.
       */
      getFTLEditorContentsAsSource: function () {
        var entity = Pontoon.getEditorEntity();
        var fallback = $('#translation').val();

        // For non-FTL entities, return unchanged translations
        if (entity.format !== 'ftl') {
          return fallback;
        }

        var translation = this.serializeTranslation(entity, fallback);

        // If translation broken, incomplete or empty
        if (translation.error) {
          return translation.error;
        }

        // Special case: empty translations in rich FTL editor don't serialize properly
        if (this.isFTLEditorEnabled()) {
          var richTranslation = $.map(
            $('#ftl-area textarea:not(".id"):visible'), function(i) {
              return $(i).val();
            }
          ).join('');

          if (!richTranslation.length) {
            translation = entity.key + ' = ';
          }
        }

        return translation;
      },


      /*
       * Render original string of FTL and non-FTL messages.
       */
      renderOriginal: function () {
        var entity = Pontoon.getEditorEntity();

        $('#original').show();
        $('#ftl-original').hide();

        if (entity.format !== 'ftl') {
          return;
        }

        $('#original').hide();
        $('#ftl-original').show();
        $('#ftl-original section ul').empty();

        var ast = fluentParser.parseEntry(entity.original);
        var unsupported = false;
        var value = '';
        var attributes = '';

        // Unsupported string: render as source
        if (!isSupportedMessage(ast)) {
          ast.comment = null; // Remove comment
          value = '<li class="source">' +
            fluentSerializer.serializeEntry(ast) +
          '</li>';

          unsupported = true;
        }

        // Simple string: only value
        else if (isSimpleMessage(ast)) {
          value = '<li><p>' +
            stringifyElements(ast.value.elements, true) +
          '</p></li>';
        }

        // Value
        else if (ast.value) {
          value = renderOriginalElements(ast.value.elements, 'Value');
        }

        // Attributes
        if (ast.attributes.length && !unsupported) {
          ast.attributes.forEach(function (attr) {
            attributes += renderOriginalElements(attr.value.elements, attr.id.name);
          });
        }

        $('#ftl-original .attributes ul').append(attributes);
        $('#ftl-original .main-value ul').append(value);
      },


      /*
       * Render form-based FTL editor. Different widgets are displayed depending on the source
       * string and the translation.
       */
      renderEditor: function (translation) {
        var self = this;
        var entity = Pontoon.getEditorEntity();
        var value = '';
        var attributes = '';
        var attributesTree = [];

        var entityAST = fluentParser.parseEntry(entity.original);
        if (entityAST.attributes.length) {
          attributesTree = entityAST.attributes;
        }

        translation = translation || entity.translation[0];
        var translationAST = null;
        if (translation.pk) {
          translationAST = fluentParser.parseEntry(translation.string);
          attributesTree = translationAST.attributes;
        }

        // Reset default editor values
        $('#ftl-area > .main-value').show().find('textarea').val('');
        $('#ftl-area > .main-value ul li:not(":first")').remove();
        $('#ftl-area .attributes ul:first').empty();
        $('#only-value').parents('li').hide();

        // Unsupported translation or unsuppported original: show source view
        if (
          (translationAST && !isSupportedMessage(translationAST)) ||
          (!translationAST && !isSupportedMessage(entityAST))
        ) {
          value = entity.key + ' = ';

          if (translationAST) {
            value = translation.string;
          }

          $('#translation').val(value);

          self.toggleEditor(false);
          Pontoon.updateCachedTranslation();

          return;
        }

        // Simple string: only value
        else if (
          (translationAST && isSimpleMessage(translationAST)) ||
          (!translationAST && isSimpleMessage(entityAST))
        ) {
          value = '';

          if (translationAST) {
            value = stringifyElements(translationAST.value.elements);
          }

          $('#only-value')
            .val(value)
            .parents('li')
            .show();
        }

        // Value
        else if (
          (translationAST && translationAST.value) ||
          entityAST.value
        ) {
          var ast = translationAST || entityAST;
          value = renderEditorElements(ast.value.elements, 'Value', translationAST);

          $('#ftl-area .main-value ul').append(value);
        }

        // No value in source string: no value in translation
        else {
          $('#ftl-area > .main-value').hide();
        }

        // Attributes
        if (attributesTree.length) {
          attributesTree.forEach(function (attr) {
            var id = attr.id.name;

            attributes += (
              '<li data-id="' + id + '">' +
                '<ul>' +
                  renderEditorElements(attr.value.elements, id, translationAST) +
                '</ul>' +
              '</li>'
            );
          });

          $('#ftl-area .attributes ul:first').append(attributes);

          // Update access keys presentation
          $('#ftl-area textarea.value').keyup();
        }

        // Ignore editing for anonymous users
        if (!Pontoon.user.id) {
          $('#ftl-area textarea').prop('readonly', true);
        }

        // Focus first field of the FTL editor
        $('#ftl-area textarea:not(".id"):visible').first().focus();

        toggleEditorToolbar();

        Pontoon.moveCursorToBeginning();
        Pontoon.updateCurrentTranslationLength();
        Pontoon.updateInPlaceTranslation();

        return true;
      },


      /*
       * Get AST and any errors for the entity's translation
       */
      serializeTranslation: function (entity, translation) {
        if (entity.format !== 'ftl') {
          return translation;
        }

        var entityAST = fluentParser.parseEntry(entity.original);
        var content = entity.key + ' = ';
        var valueElements = $('#ftl-area .main-value ul:first > li:visible');
        var attributeElements = $('#ftl-area .attributes ul:first > li:visible');
        var value = '';
        var attributes = '';

        // Unsupported string
        if (!this.isFTLEditorEnabled()) {
          content = translation;
        }

        // Simple string
        else if (!this.isComplexFTL()) {
          value = $('#only-value').val();

          // Multiline strings: mark with indent
          if (value.indexOf('\n') !== -1) {
            value = '\n  ' + value.replace(/\n/g, '\n  ');
          }

          content += value;
        }

        // Value
        else if (valueElements.length) {
          value = serializeFTLEditorElements(valueElements);

          if (value) {
            content += value;
          }
        }

        // Attributes
        if (attributeElements.length) {
          attributeElements.each(function () {
            var id = $(this).data('id');
            var val = serializeFTLEditorElements($(this).find('ul:first > li'));

            if (id && val) {
              attributes += '\n  .' + id + ' = ' + val;
            }
          });

          if (attributes) {
            content = (value ? content : entity.key) + attributes;
          }
        }

        var ast = fluentParser.parseEntry(content);
        var error = runChecks(ast, entityAST);

        if (error) {
          return {
            error: error,
          };
        }

        return fluentSerializer.serializeEntry(ast);
      },


      /*
       * Get simplified preview of the FTL message, used when full presentation not possible
       * due to lack of real estate (e.g. string list).
       */
      getSimplePreview: function (object, fallback, entity) {
        var response = fallback;

        if (entity.format === 'ftl') {
          // Transfrom complex FTL-based strings into single-value strings
          var source = object.original || object.string;

          if (!source) {
            return fallback;
          }

          var ast = fluentParser.parseEntry(source);
          var tree;

          // Value: use entire AST
          if (ast.value) {
            tree = ast;
          }

          // Attributes (must be present in valid AST if value isn't):
          // use AST of the first attribute
          else {
            tree = ast.attributes[0];
          }

          response = stringifyElements(tree.value.elements);

          // Update source string markup
          if (object.hasOwnProperty('original')) {
            response = Pontoon.doNotRender(response);
          }
        }

        return response;
      },


      /*
       * Attach event handlers to FTL editor elements
       */
      attachFTLEditorHandlers: function () {
        var self = this;

        // Ignore editing for anonymous users
        if (!Pontoon.user.id) {
          return;
        }

        // Toggle FTL and source editors
        $('#ftl').click(function (e) {
          e.preventDefault();

          var entity = Pontoon.getEditorEntity();
          var translation = null;

          // Update FTL editor
          if ($(this).is('.active')) {
            translation = $('#translation').val();

            // Strip trailing newlines for easier translated status detection
            translation = translation.replace(/\n$/, '');

            var translated = (translation && translation !== entity.key + ' = ');

            // Perform error checks
            if (translated) {
              var translationAST = fluentParser.parseEntry(translation);
              var entityAST = fluentParser.parseEntry(entity.original);
              var error = runChecks(translationAST, entityAST);
              if (error) {
                return Pontoon.endLoader(error, 'error', 5000);
              }
            }

            var isRichEditorSupported = self.renderEditor({
              pk: translated, // An indicator that the string is translated
              string: translation,
            });

            // Rich FTL editor does not support the translation
            if (!isRichEditorSupported) {
              return;
            }
          }
          // Update source editor
          else {
            translation = self.serializeTranslation(entity, translation);

            // If translation broken, incomplete or empty
            if (translation.error) {
              translation = entity.key + ' = ';
            }

            $('#translation').val(translation);
            Pontoon.updateCachedTranslation();
          }

          self.toggleEditor($(this).is('.active'));
        });

        // Generate access key candidates
        $('#ftl-area').on('keyup', 'textarea', function () {
          var accessKeyExists = $('#ftl-area .attributes [data-id="accesskey"]').length;
          var isLabel = $(this).parents('.attributes [data-id="label"]').length;
          var isValue = $(this).parents('.main-value').length;
          var generateAccessKeys = accessKeyExists && (isLabel || isValue);

          // Quit early if the element doesn't have impact on the access key
          if (!generateAccessKeys) {
            return;
          }

          // Select textarea elements to generate access key candidates from
          var content = '';
          var selector = '.main-value';
          if (isLabel) {
            selector = '.attributes [data-id="label"]';
          }

          // Build artificial FTL Message from textarea contents to only take
          // TextElements into account when generating access key candidates.
          // See bug 1447103 for more detals.
          $('#ftl-area ' + selector + ' textarea').each(function() {
            var value = $(this).val();
            var message = 'key = ' + value;
            var ast = fluentParser.parseEntry(message);

            if (ast.type !== 'Junk') {
              value = '';
              ast.value.elements.forEach(function (element) {
                if (element.type === 'TextElement') {
                  value += element.value;
                }
              });
            }

            content += value
              .replace(/\s/g, ''); // Remove whitespace
          });

          // Extract unique candidates in a list
          var candidates = content.split('')
            .filter(function (item, i, ar) {
              return ar.indexOf(item) === i;
            });

          // Store currently selected access key
          var active = $('#ftl-id-accesskey').val();

          // Reset a list of access key candidates
          $('.accesskeys').empty();

          // Render candidates
          candidates.forEach(function (candidate) {
            $('.accesskeys').append(
              '<div' + ((candidate === active) ? ' class="active"' : '') + '>' + candidate + '</div>'
            );
          });
        });

        // Select access key via click
        $('#ftl-area .attributes').on('click', '.accesskeys div', function () {
          var selected = $(this).is('.active');
          $('.accesskeys div').removeClass('active');

          if (!selected) {
            $(this).addClass('active');
          }

          $('#ftl-id-accesskey').val($('.accesskeys div.active').html());
        });

        // Select access key using text input
        $('#ftl-area .attributes').on('keyup', '#ftl-id-accesskey', function () {
          var accesskey = $(this).val();

          if (accesskey) {
            $('.accesskeys div').removeClass('active');
            $('.accesskeys div:contains("' + accesskey + '")').addClass('active');
          }
        });
      }

    },
  });
}(Pontoon || {}));
