/* global FluentSyntax */

/* Public functions used across different files */
var Pontoon = (function (my) {
  var fluentParser = new FluentSyntax.FluentParser({ withSpans: false });
  var fluentSerializer = new FluentSyntax.FluentSerializer();

  // TODO: Replace with fluentSerializer.serializeExpression() on fluent.js 0.6 update
  function serializeExpression(expression) {
    switch (expression.type) {
      case 'MessageReference':
        return expression.id.name;
      case 'ExternalArgument':
        return '$' + expression.id.name;
      case 'NumberExpression':
        return expression.value || expression.val.value;
      case 'StringExpression':
        return '"' + (expression.value || expression.val.value) + '"';
      case 'NamedArgument':
        return expression.name.name + ': ' + serializeExpression(expression.val);
      case 'CallExpression':
        var args = expression.args.map(function (arg) {
          return serializeExpression(arg);
        });
        return expression.callee.name + '(' + args.join(', ') + ')';
    }
  }

  /*
   * Render original string element: simple string value or a variant.
   */
  function renderOriginalElement(value, elements) {
    return '<li>' +
      '<span class="id">' +
        value +
      '</span>' +
      '<span class="value">' +
        Pontoon.fluent.serializePlaceables(elements, true) +
      '</span>' +
    '</li>';
  }

  /*
   * Render editor element: simple string value or a variant.
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

    var value = isTranslated ? Pontoon.fluent.serializePlaceables(elements) : '';
    var textarea = Pontoon.fluent.getTextareaElement(title, value, maxlength);

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
   * Render original string elements.
   *
   * - Adjoining simple elements are concatenated and presented as a simple string
   * - SelectExpression elements are presented as a list of variants
   */
  function renderOriginalElements(elements, title) {
    var content = '';
    var simpleElements = [];

    elements.forEach(function (element, i) {
      var isSimpleElement = Pontoon.fluent.isSimpleElement(element);
      var isLastElement = i === elements.length - 1;

      // Collect simple elements
      if (isSimpleElement) {
        simpleElements.push(element);
      }

      // Render collected simple elements when non-simple or last element is met
      if ((!isSimpleElement || isLastElement) && simpleElements.length) {
        content += renderOriginalElement(title, simpleElements);
        simpleElements = [];
      }

      // Render SelectExpression
      if (element.type === 'SelectExpression') {
        element.variants.forEach(function (item) {
          content += renderOriginalElement(item.key.value || item.key.name, item.value.elements);
        });
      }
    });

    return content;
  }

  /*
   * Render editor elements.
   *
   * - Adjoining simple elements are concatenated and presented as a simple string
   * - SelectExpression elements are presented as a list of variants
   */
  function renderEditorElements(elements, title, isTranslated) {
    var content = '';
    var simpleElements = [];

    elements.forEach(function (element, i) {
      var isSimpleElement = Pontoon.fluent.isSimpleElement(element);
      var isLastElement = i === elements.length - 1;

      // Collect simple elements
      if (isSimpleElement) {
        simpleElements.push(element);
      }

      // Render collected simple elements when non-simple or last element is met
      if ((!isSimpleElement || isLastElement) && simpleElements.length) {
        content += renderEditorElement(title, simpleElements, false, isTranslated);
        simpleElements = [];
      }

      // Render SelectExpression
      if (element.type === 'SelectExpression') {
        var expression = serializeExpression(element.expression);
        content = '<li data-expression="' + expression + '"><ul>' + content;

        var isPlural = Pontoon.fluent.isPluralElement(element);
        if (isPlural && !isTranslated) {
          Pontoon.locale.cldr_plurals.forEach(function (pluralName) {
            content += renderEditorElement(pluralName, [], true, isTranslated);
          });
        }
        else {
          element.variants.forEach(function (item) {
            content += renderEditorElement(
              item.key.value || item.key.name,
              item.value.elements,
              isPlural,
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
   * Serialize values in FTL editor forms into an FTL string.
   */
  function serializeElements(elements) {
    var value = '';

    elements.each(function (i, element) {
      var expression = $(element).data('expression');

      // Simple element
      if (!expression) {
        value += $(this).find('textarea').val();
      }

      // SelectExpression
      else {
        var elementValue = expression + ' ->';
        var variants = $(element).find('ul li');
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
            elementValue += '\n  ' + defaultMarker + '[' + id + '] ' + val;
            hasTranslatedVariants = true;
          }
        });

        if (hasTranslatedVariants) {
          value += '{ ' + elementValue + '\n  }';
        }
      }
    });

    return value;
  }

  return $.extend(true, my, {
    fluent: {

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
          (translationAST && !self.isSupportedMessage(translationAST)) ||
          (!translationAST && !self.isSupportedMessage(entityAST))
        ) {
          value = entity.key + ' = \n';

          if (translationAST) {
            value = translation.string;
          }

          $('#translation').val(value);

          Pontoon.fluent.toggleEditor(false);
          Pontoon.updateCachedTranslation();

          return;
        }


        // Simple string: only value
        else if (
          (translationAST && self.isSimpleString(translationAST)) ||
          (!translationAST && self.isSimpleString(entityAST))
        ) {
          value = '';

          if (translationAST) {
            value = self.serializePlaceables(translationAST.value.elements);
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
          $('#ftl-area .attributes textarea').keyup();
        }

        // Ignore editing for anonymous users
        if (!Pontoon.user.id) {
          $('#ftl-area textarea').prop('readonly', true);
        }

        Pontoon.fluent.focusFirstField();
        Pontoon.fluent.toggleEditorToolbar();

        Pontoon.moveCursorToBeginning();
        Pontoon.updateCurrentTranslationLength();
        Pontoon.updateInPlaceTranslation();

        return true;
      },


      /*
       * Is ast of a message, supported in rich FTL editor?
       *
       * Message is supported if all value elements
       * and all attribute elements are of type:
       * - TextElement
       * - ExternalArgument
       * - MessageReference
       * - SelectExpression?
       */
      isSupportedMessage: function (ast) {
        function elementsSupported(elements) {
          return elements.every(function(item) {
            return [
              'TextElement',
              'ExternalArgument',
              'MessageReference',
              'SelectExpression'
            ].indexOf(item.type) >= 0;
          });
        }

        // Parse error
        if (ast.type === 'Junk') {
          return false;
        }

        var valueSupported = !ast.value || elementsSupported(ast.value.elements);
        var attributesSupported = ast.attributes.every(function (attribute) {
          return attribute.value && elementsSupported(attribute.value.elements);
        });

        return valueSupported && attributesSupported;
      },


      /*
       * Is element of type that can be presented as a simple string:
       * - TextElement
       * - ExternalArgument
       * - MessageReference
       */
      isSimpleElement: function (element) {
        return [
          'TextElement',
          'ExternalArgument',
          'MessageReference'
        ].indexOf(element.type) >= 0;
      },


      /*
       * Is ast of a simple string?
       *
       * A simple string has no attributes or tags,
       * and the value can only contain text and
       * references to external arguments or other messages.
       */
      isSimpleString: function (ast) {
        var self = this;

        if (
          ast &&
          !ast.attributes.length &&
          !ast.tags.length &&
          ast.value &&
          ast.value.elements.every(function(item) {
            return self.isSimpleElement(item);
          })
        ) {
          return true;
        }

        return false;
      },


      /*
       * Is element representing a pluralized string?
       *
       * Keys of all variants of such elements are either
       * CLDR plurals or numbers.
       */
      isPluralElement: function (element) {
        if (!element.variants) {
          return false;
        }

        var CLDRplurals = ['zero', 'one', 'two', 'few', 'many', 'other'];

        return element.variants.every(function (item) {
          return (
            CLDRplurals.indexOf(item.key.name) !== -1 ||
            item.key.type === 'NumberExpression'
          );
        });
      },


      /*
       * Serialize value with placeables into a simple string
       *
       * markPlaceables Should placeables be marked up?
       */
      serializePlaceables: function (elements, markPlaceables) {
        var self = this;
        var translatedValue = '';
        var startMarker = '';
        var endMarker = '';

        elements.forEach(function (item) {
          if (item.type === 'TextElement') {
            if (markPlaceables) {
              translatedValue += Pontoon.markXMLTags(item.value);
            }
            else {
              translatedValue += item.value;
            }
          }
          else if (item.type === 'ExternalArgument') {
            if (markPlaceables) {
              startMarker = '<mark class="placeable" title="External Argument">';
              endMarker = '</mark>';
            }
            translatedValue += startMarker + '{$' + item.id.name + '}' + endMarker;
          }
          else if (item.type === 'MessageReference') {
            if (markPlaceables) {
              startMarker = '<mark class="placeable" title="Message Reference">';
              endMarker = '</mark>';
            }
            translatedValue += startMarker + '{' + item.id.name + '}' + endMarker;
          }
          else if (item.variants) {
            var variantElements = item.variants.filter(function (item) {
              return item.default;
            })[0].value.elements;

            translatedValue += self.serializePlaceables(variantElements);
          }
        });

        return translatedValue;
      },


      /*
       * Generate textarea element with the given properties
       */
      getTextareaElement: function (id, value, maxlength) {
        var base = '<textarea class="value" id="ftl-id-' + id + '"';

        if (typeof maxlength !== 'undefined' && maxlength !== null) {
          base += ' maxlength="' + maxlength + '"';
        }

        base += ' dir="' + Pontoon.locale.direction +
          '" data-script="' + Pontoon.locale.script +
          '" lang="' + Pontoon.locale.code + '">' + value + '</textarea>';
        return base;
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

          // TODO: Uncomment once attributes are fully supported (defaults, removing, validation)
          // $('#add-attribute').show();
        }
        else {
          $('#ftl-area').hide();
          $('#translation').show().focus();
          $('#ftl').addClass('active');

          // TODO: Uncomment once attributes are fully supported (defaults, removing, validation)
          // $('#add-attribute').hide();
        }

        Pontoon.fluent.toggleEditorToolbar();
        Pontoon.moveCursorToBeginning();
      },


      /*
       * Toggle translation length and Copy button in editor toolbar
       */
      toggleEditorToolbar: function () {
        var entity = Pontoon.getEditorEntity();
        var show = entity.format !== 'ftl' || !Pontoon.fluent.isComplexFTL();

        $('#translation-length, #copy').toggle(show);

        if ($('#translation-length').is(':visible')) {
          var original = this.getSimplePreview(entity, entity.original, entity);
          $('#translation-length').find('.original-length').html(original.length);
        }
      },


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
       * Toggle between source and FTL display of the original string
       */
      toggleOriginal: function () {
        var self = this;
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
        if (!self.isSupportedMessage(ast)) {
          ast.comment = null; // Remove comment
          value = '<li class="source">' +
            fluentSerializer.serializeEntry(ast) +
          '</li>';

          unsupported = true;
        }

        // Simple string: only value
        else if (self.isSimpleString(ast)) {
          value = '<li><p>' +
            self.serializePlaceables(ast.value.elements, true) +
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
       * Return translation in the editor as FTL source
       */
      getTranslationSource: function () {
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
            translation = entity.key + ' = \n';
          }
        }

        return translation;
      },


      /*
       * Get AST and any errors for the entity's translation
       */
      serializeTranslation: function (entity, translation) {
        if (entity.format !== 'ftl') {
          return translation;
        }

        var entityAST = fluentParser.parseEntry(entity.original);
        var content = entity.key + ' = '; // Initialize untranslated string
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
          value = serializeElements(valueElements);

          if (value) {
            content += value;
          }
        }

        // Attributes
        if (attributeElements.length) {
          attributeElements.each(function () {
            var id = $(this).data('id');
            var val = serializeElements($(this).find('ul:first > li'));

            if (id && val) {
              attributes += '\n  .' + id + ' = ' + val;
            }
          });

          if (attributes) {
            content = (value ? content : entity.key) + attributes;
          }
        }

        var ast = fluentParser.parseEntry(content);
        var error = null;

        // Parse error
        if (ast.type === 'Junk') {
          error = ast.annotations[0].message;
        }
        // TODO: Should be removed by bug 1237667
        // Detect missing values
        else if (entityAST && ast && entityAST.value && !ast.value) {
          error = 'Please make sure to fill in the value';
        }
        // Detect missing attributes
        else if (
          entityAST.attributes &&
          ast.attributes &&
          entityAST.attributes.length !== ast.attributes.length
        ) {
          error = 'Please make sure to fill in all the attributes';
        }

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

          response = this.serializePlaceables(tree.value.elements);

          // Update source string markup
          if (object.hasOwnProperty('original')) {
            response = Pontoon.doNotRender(response);
          }
        }

        return response;
      },


      /*
       * Get source string value of a simple FTL message
       */
      getSourceStringValue: function (entity, fallback) {
        if (entity.format !== 'ftl' || this.isComplexFTL()) {
          return fallback;
        }

        var ast = fluentParser.parseEntry(entity.original);
        return this.serializePlaceables(ast.value.elements);
      },


      /*
       * Focus first field of the FTL editor
       */
      focusFirstField: function () {
        $('#ftl-area textarea:not(".id"):visible').first().focus();
      },

    },
  });
}(Pontoon || {}));

$(function () {

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

      var isRichEditorSupported = Pontoon.fluent.renderEditor({
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
      translation = Pontoon.fluent.serializeTranslation(entity, translation);

      // If translation broken, incomplete or empty
      if (translation.error) {
        translation = entity.key + ' = \n';
      }

      $('#translation').val(translation);
      Pontoon.updateCachedTranslation();
    }

    Pontoon.fluent.toggleEditor($(this).is('.active'));
  });

  // Add attribute
  $('#add-attribute').click(function (e) {
    e.preventDefault();
    $('#ftl-area .attributes ul:first').append($('#ftl-area .attributes .template li').clone());
  });

  // Generate access key list
  $('#ftl-area .attributes').on('keyup', 'textarea:first', function () {
    var active = $('.accesskeys').find('.active').html();
    var unique = $(this).val()
      .toUpperCase()
      .split('')
      .filter(function (item, i, ar) {
        return ar.indexOf(item) === i;
      });

    $('.accesskeys').empty();

    $.each(unique, function (i, v) {
      $('.accesskeys').append(
        '<div' + ((v === active) ? ' class="active"' : '') + '>' + v + '</div>'
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
    var accesskey = $(this).val().toUpperCase();

    if (accesskey) {
      $('.accesskeys div').removeClass('active');
      $('.accesskeys div:contains("' + accesskey + '")').addClass('active');
    }
  });

});
