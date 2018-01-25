/* global FluentSyntax */

/* Public functions used across different files */
var Pontoon = (function (my) {
  var fluentParser = new FluentSyntax.FluentParser({ withSpans: false });
  var fluentSerializer = new FluentSyntax.FluentSerializer();

  function renderPluralEditor(value, name, pluralIndex) {
    var example = Pontoon.locale.examples[pluralIndex];

    $('#ftl-area .main-value ul')
      .append(
        '<li class="clearfix">' +
          '<label class="id" for="ftl-id-' + name + '">' +
            '<span>' + name + '</span>' +
            (Pontoon.fluent.isCLDRplural(name) && example !== undefined ? '<span> (e.g. ' +
              '<span class="stress">' + example + '</span>' +
            ')</span>' : '') +
            '<sub class="fa fa-remove remove" title="Remove"></sub>' +
          '</label>' +
          Pontoon.fluent.getTextareaElement(name, value) +
        '</li>'
      );
  }

  function renderOriginalVariant(value, elements) {
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
        content += renderOriginalVariant(title, simpleElements);
        simpleElements = [];
      }

      // Render SelectExpression
      if (element.type === 'SelectExpression') {
        element.variants.forEach(function (item) {
          content += renderOriginalVariant(item.key.value || item.key.name, item.value.elements);
        });
      }
    });

    return content;
  }

  return $.extend(true, my, {
    fluent: {

      /*
       * Render form-based FTL editor. Different widgets are displayed depending on the source
       * string and the translation.
       */
      renderEditor: function (translation) {
        $('#ftl-area > .main-value').show().find('textarea').val('');
        $('#ftl-area .attributes ul:first').empty();
        $('#ftl-area > .main-value ul li:not(":first")').remove();
        $('#only-value').parents('li').hide();

        var self = this;
        var entity = Pontoon.getEditorEntity();

        translation = translation || entity.translation[0];

        var isTranslated = translation.pk;
        var entityAST = fluentParser.parseEntry(entity.original);
        var entityAttributes = [];
        var attributes = entityAST.attributes;

        var translationAST;
        if (isTranslated) {
          translationAST = fluentParser.parseEntry(translation.string);
          attributes = translationAST.attributes;
        }

        if (entityAST.attributes) {
          entityAttributes = entityAST.attributes.map(function (item) {
            return item.id.name;
          });
        }

        // Simple string: only value
        if (
          self.isSimpleString(translationAST) ||
          self.isSimpleString(entityAST)
        ) {
          var value = '';

          if (translationAST) {
            value = self.serializePlaceables(translationAST.value.elements);
          }

          $('#only-value')
            .val(value)
            .parents('li')
            .show();
        }
        // Plurals
        else if (self.isPlural(entityAST)) {
          var pluralForms = Pontoon.locale.cldr_plurals.map(function (item) {
            return Pontoon.CLDR_PLURALS[item];
          });

          if (!Pontoon.locale.examples) {
            Pontoon.generateLocalePluralExamples();
          }

          // Translated
          if (translationAST) {
            translationAST.value.elements[0].variants.forEach(function (variant, i) {
              var value = self.serializePlaceables(variant.value.elements);
              var name = variant.key.name || variant.key.value;
              var pluralIndex = pluralForms.findIndex(function(item) {
                return item === name;
              });

              renderPluralEditor(value, name, pluralIndex);
            });
          }
          // Untranslated
          else {
            pluralForms.forEach(function (pluralName, pluralIndex) {
              var value = '';
              var name = pluralName;

              renderPluralEditor(value, name, pluralIndex);
            });
          }
        }
        // Value and attributes
        else if (entityAST && entityAST.value && entityAST.attributes.length) {
          var value = isTranslated ? self.serializePlaceables(translationAST.value.elements) : '';

          $('#ftl-area .main-value ul')
            .append(
              '<li class="clearfix">' +
                '<label class="id" for="ftl-id-value">Value</label>' +
                Pontoon.fluent.getTextareaElement('value', value) +
              '</li>'
            );
        }
        // Attributes
        if (attributes && attributes.length) {
          attributes.forEach(function (attr) {
            var id = attr.id.name;
            var value = isTranslated ? self.serializePlaceables(attr.value.elements) : '';

            var maxlength = '';
            var label = '';
            var textarea = '';
            var cls = '';

            if (id === 'accesskey') {
              maxlength = '1';
              textarea = '<div class="accesskeys"></div>';
            }
            textarea += self.getTextareaElement(id, value, maxlength);

            if ($.inArray(id, [entityAttributes])) {
              label = '<label class="id" for="ftl-id-' + id + '">' +
                '<span>' + id + '</span>' +
              '</label>';

            }
            else {
              cls = ' class="custom-attribute clearfix"';
              label = '<div class="wrapper">' +
                '<textarea class="id" placeholder="enter-attribute-id">' + id + '</textarea>' +
                '<sub class="fa fa-remove remove" title="Remove"></sub>' +
              '</div>';
            }

            $('#ftl-area .attributes ul:first')
              .append(
                '<li' + cls + '>' +
                  label +
                  textarea +
                '</li>'
              );
          });

          // Update access keys presentation
          $('#ftl-area .attributes textarea').keyup();

        }

        // Show source editor if source string is displayed as source
        if ($('#ftl-original .main-value ul li.source').length) {
          var value = entity.key + ' = \n';

          if (isTranslated) {
            value = translation.string;
          }

          $('#translation').val(value);
          Pontoon.updateCachedTranslation();
          Pontoon.fluent.toggleEditor(false);
          return;
        }

        // If no value in source string, no value in translation
        if (!entityAST.value) {
          $('#ftl-area > .main-value').hide();
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
       * Is ast of a supported message?
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
       * Is CLDR plural name?
       */
      isCLDRplural: function (name) {
        return Pontoon.CLDR_PLURALS.indexOf(name) !== -1;
      },


      /*
       * Is ast of a pluralized string?
       */
      isPlural: function (ast) {
        var self = this;

        if (
          ast &&
          ast.value &&
          ast.value.elements &&
          ast.value.elements.length &&
          ast.value.elements[0].expression &&
          ast.value.elements[0].variants.every(function (element) {
            return self.isCLDRplural(element.key.name) || element.key.type === 'NumberExpression';
          })
        ) {
          return true;
        }

        return false;
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
            // TODO: We shouldn't rely on markPlaceables in determining when to not render HTML.
            if (markPlaceables) {
              translatedValue += Pontoon.doNotRender(item.value);
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

        // Simple string: only value
        if (self.isSimpleString(ast)) {
          value = '<li><p>' +
            self.serializePlaceables(ast.value.elements, true) +
          '</p></li>';
        }

        // Unsupported string: render as source
        else if (!self.isSupportedMessage(ast)) {
          ast.comment = null; // Remove comment
          value = '<li class="source">' +
            fluentSerializer.serializeEntry(ast) +
          '</li>';

          unsupported = true;
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

        if (!this.isComplexFTL()) {
          translation = $('#only-value').val();

          // Multiline strings: mark with indent
          if (translation.indexOf('\n') !== -1) {
            translation = ' = \n  ' + translation.replace(/\n/g, '\n  ');
          }
          // Simple strings
          else {
            translation = ' = ' + translation;
          }
        }
        else if (this.isFTLEditorEnabled()) {
          // Main value
          var entityAST = fluentParser.parseEntry(entity.original);
          var value = $('#ftl-area > .main-value textarea:visible').val();
          var attributes = '';

          // Plurals
          if (this.isPlural(entityAST)) {
            value = '';
            var variants = $('#ftl-area .main-value li:visible');
            var nonEmptyVariants = [];
            var def = '';

            variants.each(function () {
              var id = $(this).find('.id span:first').html().split(' ')[0];
              var val = $(this).find('.value').val();

              if (id && val) {
                nonEmptyVariants.push('[' + id + '] ' + val);
              }
            });

            nonEmptyVariants.forEach(function (variant, i) {
            // for (var i = 0; i < nonEmptyVariants.length; i++) {
              // Mark the last variant as default
              // TODO: Should be removed by bug 1237667
              if (i === nonEmptyVariants.length - 1) {
                def = '*';
              }
              value += '\n  ' + def + variant;
            });

            if (value) {
              value = '{ $' + entityAST.value.elements[0].expression.id.name + ' ->' + value + '\n  }';
            }
          }

          // Attributes
          $('#ftl-area .attributes ul:first li').each(function () {
            var id = $(this).find('.id span').html() || $(this).find('.id').val();
            var val = $(this).find('.value').val();

            if (id && val) {
              attributes += '\n  .' + id + ' = ' + val;
            }
          });

          translation = (value ? ' = ' + value : '') + (attributes || '');
        }

        var content = entity.key + translation;
        // Source view
        if (!this.isFTLEditorEnabled()) {
          content = translation;
        }

        var ast = fluentParser.parseEntry(content);
        var entityAst = fluentParser.parseEntry(entity.original);
        var error = null;

        // Parse error
        if (ast.type === 'Junk') {
          error = ast.annotations[0].message;
        }
        // TODO: Should be removed by bug 1237667
        // Detect missing values
        else if (entityAst && ast && entityAst.value && !ast.value) {
          error = 'Please make sure to fill in the value';
        }
        // Detect missing attributes
        else if (
          entityAst.attributes &&
          ast.attributes &&
          entityAst.attributes.length !== ast.attributes.length
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

  // Remove attribute
  $('#ftl-area section').on('click', 'sub.remove', function (e) {
    e.preventDefault();
    $(this).parents('li').remove();
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
