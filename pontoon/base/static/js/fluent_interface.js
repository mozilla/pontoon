/* global FluentSyntax */
var fluentParser = new FluentSyntax.FluentParser({ withSpans: false });
var fluentSerializer = new FluentSyntax.FluentSerializer();

/* Public functions used across different files */
var Pontoon = (function (my) {

  /*
   * Is ast element of type that can be presented as a simple string:
   * - TextElement
   * - Placeable with expression type CallExpression, StringLiteral, NumberLiteral,
   *   VariantExpression, AttributeExpression, VariableReference or MessageReference
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
        'StringLiteral',
        'NumberLiteral',
        'VariantExpression',
        'AttributeExpression',
        'VariableReference',
        'MessageReference'
      ].indexOf(element.expression.type) >= 0
    ) {
      return true;
    }

    return false;
  }

  /*
   * Return true when AST element represents a pluralized string.
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
        item.key.type === 'NumberLiteral'
      );
    });
  }

  /*
   * Return true when all elements are supported in rich FTL editor.
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
   * Return true when AST represents a message, supported in rich FTL editor.
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
   * Return true when AST represents a simple message.
   *
   * A simple message has no attributes and all value
   * elements are simple.
   */
  function isSimpleMessage(ast) {
    if (
      ast &&
      !ast.attributes.length &&
      ast.value &&
      ast.value.elements.every(isSimpleElement)
    ) {
      return true;
    }

    return false;
  }

  /*
   * Return true when AST has no value
   * and a single attribute with only simple elements.
   */
  function isSimpleSingleAttributeMessage(ast) {
    if (
      ast &&
      !ast.value &&
      ast.attributes.length === 1 &&
      ast.attributes[0].value.elements.every(isSimpleElement)
    ) {
      return true;
    }

    return false;
  }

  /*
   * Render textarea element with the given properties
   */
  function renderTextareaElement(id, value, maxlength) {
    var element = '<textarea class="value" id="ftl-id-' + id + '"' + ' maxlength="' + maxlength + '"';

    element += ' dir="' + Pontoon.locale.direction +
      '" data-script="' + Pontoon.locale.script +
      '" lang="' + Pontoon.locale.code + '">' + value + '</textarea>';
    return element;
  }

  /*
   * Render original string element with given title and ast elements
   */
  function renderOriginalElement(title, elements) {
    return '<li class="clearfix">' +
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
  function renderEditorElement(title, elements, isPlural, isTranslated, isCustomAttribute) {
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

    var id = '<label class="id" for="ftl-id-' + title + '">' +
      '<span>' + title + '</span>' +
      exampleSpan +
    '</label>';

    // Special case: Custom attribute
    if (isCustomAttribute) {
      id = '<div class="wrapper">' +
        '<input type="text" class="id" value="' + title + '">' +
        '<span class="fa fa-times remove" title="Remove attribute"></span>' +
      '</div>';
    }

    var value = isTranslated ? stringifyElements(elements) : '';
    var textarea = renderTextareaElement(title, value, maxlength);

    return '<li class="clearfix">' +
      id +
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
        var expression = '';
        if (element.expression.expression) {
          expression = fluentSerializer.serializeExpression(element.expression.expression);
        }
        content += '<li data-expression="' + expression + '"><ul>';

        element.expression.variants.forEach(function (item) {
          content += renderOriginalElement(item.key.value || item.key.name, item.value.elements);
        });

        content += '</ul></li>';
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
  function renderEditorElements(elements, title, isTranslated, isCustomAttribute) {
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
        content += renderEditorElement(title, simpleElements, false, isTranslated, isCustomAttribute);
        simpleElements = [];
      }

      // Render SelectExpression
      if (element.expression && element.expression.type === 'SelectExpression') {
        var expression = '';
        if (element.expression.expression) {
          expression = fluentSerializer.serializeExpression(element.expression.expression);
        }
        content += '<li data-expression="' + expression + '"><ul>';

        if (isPluralElement(element) && !isTranslated) {
          Pontoon.locale.cldr_plurals.forEach(function (pluralName) {
            content += renderEditorElement(pluralName, [], true, isTranslated, isCustomAttribute);
          });
        }
        else {
          element.expression.variants.forEach(function (item) {
            content += renderEditorElement(
              item.key.value || item.key.name,
              item.value.elements,
              isPluralElement(element),
              isTranslated,
              isCustomAttribute
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
      // Simple element
      if (!node.hasAttribute('data-expression')) {
        value += $(this).find('textarea').val();
      }

      // SelectExpression
      else {
        var expression = $(node).data('expression');
        var nodeValue = expression ? ' ' + expression + ' ->' : '';
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
          value += '{' + nodeValue + '\n  }';
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
        if (element.expression.type === 'VariableReference') {
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
        else if (
          [
            'CallExpression',
            'StringLiteral',
            'NumberLiteral',
            'VariantExpression',
            'AttributeExpression',
          ].indexOf(element.expression.type) >= 0
        ) {
          var title = element.expression.type.replace('Expression', ' Expression');
          if (markPlaceables) {
            startMarker = '<mark class="placeable" title="' + title + '">';
            endMarker = '</mark>';
          }
          var expression = fluentSerializer.serializeExpression(element.expression);
          string += startMarker + '{' + expression + '}' + endMarker;
        }
        else if (element.expression.type === 'SelectExpression') {
          var variantElements = element.expression.variants.filter(function (variant) {
            return variant.default;
          })[0].value.elements;
          string += stringifyElements(variantElements, markPlaceables);
        }
      }
    });

    return string;
  }

  /*
   * Toggle translation length and Copy button in editor toolbar
   */
  function toggleEditorToolbar() {
    var entity = Pontoon.getEditorEntity();
    var show = entity.format !== 'ftl' || !Pontoon.fluent.isComplexFTL();

    $('#translation-length, #copy').toggle(show);

    if ($('#translation-length').is(':visible')) {
      var original = Pontoon.fluent.getSimplePreview(entity.original);
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

          var entityAST = fluentParser.parseEntry(entity.original);
          $('#add-attribute').toggle(entityAST.type === 'Term');
        }
        else {
          $('#ftl-area').hide();
          $('#translation').show().focus();
          $('#ftl').addClass('active');
          $('#add-attribute').hide();
        }

        toggleEditorToolbar();
        Pontoon.moveCursorToBeginning();
      },


      /*
       * Get source string value of a simple FTL message or a simple
       * single attribute FTL message to be used in the Copy (original
       * to translation) function.
       */
      getSourceStringValue: function (entity, fallback) {
        if (entity.format !== 'ftl' || this.isComplexFTL()) {
          return fallback;
        }

        var ast = fluentParser.parseEntry(entity.original);
        var tree;

        // Simple string
        if (ast.value) {
          tree = ast;
        }
        // Simple single-attribute string
        else {
          tree = ast.attributes[0];
        }

        return stringifyElements(tree.value.elements);
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
       * Get attribute, if ast of the entity is a simple single attribute message.
       * Else: return false.
       */
      getSimpleSingleAttribute: function (entity) {
        if (entity.format !== 'ftl') {
          return false;
        }

        var ast = fluentParser.parseEntry(entity.original);

        if (!isSimpleSingleAttributeMessage(ast)) {
          return false;
        }

        return ast.attributes[0];
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
          // Simple single-attribute string
          if (isSimpleSingleAttributeMessage(ast)) {
            attributes = '<li><p>' +
              stringifyElements(ast.attributes[0].value.elements, true) +
            '</p></li>';
          }
          else {
            ast.attributes.forEach(function (attr) {
              attributes += renderOriginalElements(attr.value.elements, attr.id.name);
            });
          }
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
        var entityAttributes = [];
        var translatedAttributes = [];

        var entityAST = fluentParser.parseEntry(entity.original);
        if (entityAST.attributes.length) {
          attributesTree = entityAST.attributes;
          entityAttributes = entityAST.attributes.map(function (attr) {
            return attr.id.name;
          });
        }

        translation = translation || entity.translation[0];
        var translationAST = null;
        if (translation.pk) {
          translationAST = fluentParser.parseEntry(translation.string);
          attributesTree = translationAST.attributes;

          // If translation doesn't include all entity attributes,
          // we need to manually add them
          translatedAttributes = attributesTree.map(function (attr) {
            return attr.id.name;
          });
          entityAST.attributes.forEach(function (attr) {
            if (translatedAttributes.indexOf(attr.id.name) === -1) {
              attributesTree.push(attr);
            }
          });
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
          value = renderEditorElements(ast.value.elements, 'Value', translationAST, false);

          $('#ftl-area .main-value ul').append(value);
        }

        // No value in source string: no value in translation
        else {
          $('#ftl-area > .main-value').hide();
        }

        // Attributes
        if (attributesTree.length) {
          // Simple single-attribute string: only attribute
          if (
            (translationAST && isSimpleSingleAttributeMessage(translationAST)) ||
            (!translationAST && isSimpleSingleAttributeMessage(entityAST))
          ) {
            value = '';

            if (translationAST) {
              value = stringifyElements(translationAST.attributes[0].value.elements);
            }

            $('#only-value')
              .val(value)
              .parents('li')
              .show();

            $('#ftl-area > .main-value').show();
          }
          else {
            attributesTree.forEach(function (attr) {
              var id = attr.id.name;

              // Mark translated attributes
              var isTranslated = translatedAttributes.indexOf(id) !== -1;

              // Custom attributes
              var identifier = 'data-id="' + id + '"';
              var isCustomAttribute = false;
              if (entityAttributes.indexOf(attr.id.name) === -1) {
                identifier = 'class="custom-attribute"';
                isCustomAttribute = true;
              }

              attributes += (
                '<li ' + identifier + '>' +
                  '<ul>' +
                    renderEditorElements(attr.value.elements, id, isTranslated, isCustomAttribute) +
                  '</ul>' +
                '</li>'
              );
            });

            $('#ftl-area .attributes ul:first').append(attributes);

            // Update access keys presentation
            $('#ftl-area textarea.value').keyup();
          }
        }

        // Indent selector variants if preceeded by other elements
        $('.ftl-area section > ul:not(.template) > li[data-expression]').each(function(i, node) {
          if ($(node).prevAll(':visible:not([data-expression])').length) {
            $(node).addClass('indented');
          }
        });

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

          // Simple single-attribute string
          var attribute = $('#metadata .attribute .content').text();
          if (attribute) {
            value = '\n  .' + attribute + ' = ' + value;
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
            // Entity or custom attribute
            var id = $(this).data('id') || $(this).find('.id').val();
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

        return fluentSerializer.serializeEntry(ast);
      },


      /*
       * Get simplified preview of the FTL message, used when full presentation not possible
       * due to lack of real estate (e.g. string list).
       */
      getSimplePreview: function (source, fallback, markPlaceables) {
        source = source || '';
        fallback = fallback || source;
        var ast = fluentParser.parseEntry(source);

        // String with an error
        if (ast.type === 'Junk') {
          return fallback;
        }

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

        return stringifyElements(tree.value.elements, markPlaceables);
      },


      /*
       * Attach event handlers to FTL editor elements
       */
      attachFTLEditorHandlers: function () {
        var self = this;

        // Toggle FTL and source editors
        $('#ftl').click(function (e) {
          e.preventDefault();

          var entity = Pontoon.getEditorEntity();
          var translation = $('#translation').val();

          $.ajax({
            url: '/perform-checks/',
            type: 'POST',
            data: {
              csrfmiddlewaretoken: $('#server').data('csrf'),
              entity: entity.pk,
              locale_code: Pontoon.locale.code,
              original: entity.original,
              string: self.serializeTranslation(entity, translation),
              ignore_warnings: false,
            },
            success: function(data) {
              var showFTLEditor = $('#ftl').is('.active');
              if (!showFTLEditor) {
                translation = self.serializeTranslation(entity, translation);
              }

              // If non-empty translation broken or incomplete: prevent switching
              var translated = translation !== entity.key + ' = ';
              if (translated && data.failedChecks) {
                return Pontoon.renderFailedChecks(data.failedChecks, true);
              }

              // Update editor contents
              if (showFTLEditor) {
                var isRichEditorSupported = self.renderEditor({
                  pk: translated, // An indicator that the string is translated
                  string: translation,
                });

                // Rich FTL editor does not support the translation
                if (!isRichEditorSupported) {
                  return Pontoon.endLoader('Translation not supported in rich editor', 'error');
                }
              }
              else {
                $('#translation').val(translation);
                Pontoon.updateCachedTranslation();
              }

              self.toggleEditor(showFTLEditor);
            }
          });
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
          if (Pontoon.isReadonlyEditor()) {
            return;
          }

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

        // Add an attribute
        $('#add-attribute').click(function (e) {
          e.preventDefault();

          var attributeTemplate = $('#ftl-area .templates .attribute').html();
          $('#ftl-area .attributes ul:first').append(attributeTemplate);

          // Simple string: convert to complex
          if (!self.isComplexFTL()) {
            var value = $('#only-value').val();
            var valueTemplate = $('#ftl-area .templates .value').html();

            $('#ftl-area .main-value ul:first').append(valueTemplate);
            $('#ftl-id-Value').val(value);
            $('#only-value').parents('li').hide();
          }
        });

        // Remove an attribute
        $('#ftl-area .attributes').on('click', '.custom-attribute .remove', function (e) {
          e.preventDefault();

          if (Pontoon.isReadonlyEditor()) {
            return;
          }

          $(this).parents('.custom-attribute').remove();

          // Simple value only: convert to simple string
          var valueElements = $('#ftl-area .main-value ul:first > li:visible');
          var variants = valueElements.is('[data-expression]');
          var attributeElements = $('#ftl-area .attributes ul:first > li:visible');

          if (valueElements.length === 1 && !variants && !attributeElements.length) {
            var value = $('#ftl-id-Value').val();

            $('#ftl-id-Value').parents('li').remove();
            $('#only-value')
              .val(value)
              .parents('li').show();
          }
        });
      }

    },
  });
}(Pontoon || {}));
