/* global FluentSyntax */

/* Public functions used across different files */
var Pontoon = (function (my) {
  var fluentParser = new FluentSyntax.FluentParser({ withSpans: false });
  var fluentSerializer = new FluentSyntax.FluentSerializer();

  return $.extend(true, my, {
    fluent: {

      /*
       * Render form-based FTL editor. Different widgets are displayed depending on the source
       * string and the translation.
       */
      renderEditor: function (translation) {
        $('#ftl-area > .main-value').show().find('input').val('');
        $('#ftl-area .attributes ul:first').empty();
        $('#ftl-area > .main-value ul li:not(":first")').remove();

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
        else if (entity.isFTLplural) {
          var pluralForms = Pontoon.locale.cldr_plurals.map(function (item) {
            return Pontoon.CLDR_PLURALS[item];
          });

          var variants;
          if (translationAST) {
            variants = translationAST.value.elements[0].variants;
          }

          if (!Pontoon.locale.examples) {
            Pontoon.generateLocalePluralExamples();
          }

          pluralForms.forEach(function (pluralStr, pluralInt) {
            var value = '';

            if (translationAST) {
              for (var i = 0; i < variants.length; i++) {
                if (variants[i].key.name === pluralStr) {
                  value = self.serializePlaceables(variants[i].value.elements);
                  break;
                }
              }
            }

            $('#ftl-area .main-value ul')
              .append(
                '<li class="clearfix">' +
                  '<label class="id built-in" for="ftl-id-' + pluralStr + '">' +
                    '<span>' + pluralStr + ' (e.g. </span>' +
                    '<span class="stress">' + Pontoon.locale.examples[pluralInt] + '</span>)' +
                    '<sub class="fa fa-remove remove" title="Remove"></sub>' +
                  '</label>' +
                  self.inputValueElement(pluralStr, value) +
                '</li>'
              );
          });

          $('#only-value').parents('li').hide();
        }
        // Attributes
        else if (attributes && attributes.length) {
          attributes.forEach(function (attr) {
            var id = attr.id.name;
            var value = isTranslated ? self.serializePlaceables(attr.value.elements) : '';

            var maxlength = '';
            var label = '';
            var input = '';
            var cls = '';

            if (id === 'accesskey') {
              maxlength = '1';
              input = '<div class="accesskeys"></div>';
            }
            input += self.inputValueElement(id, value, maxlength);

            if ($.inArray(id, [entityAttributes])) {
              label = '<label class="id" for="ftl-id-' + id + '">' +
                '<span>' + id + '</span>' +
              '</label>';

            }
            else {
              cls = ' class="custom-attribute clearfix"';
              label = '<div class="wrapper">' +
                '<input type="text" class="id" placeholder="enter-attribute-id" value="' + id + '">' +
                '<sub class="fa fa-remove remove" title="Remove"></sub>' +
              '</div>';
            }

            $('#ftl-area .attributes ul:first')
              .append(
                '<li' + cls + '>' +
                  label +
                  input +
                '</li>'
              );
          });

          // Update access keys presentation
          $('#ftl-area .attributes input').keyup();

        }
        // Show source if rich FTL editor does not support the translation or
        // if translation is not available and source string is displayed as source
        else if ($('#ftl-original .main-value ul li.source').length) {
          var value = entity.key + ' = ';

          if (isTranslated) {
            value = translation.string;
          }

          $('#translation').val(value);
          Pontoon.fluent.toggleEditor(false);
          return;
        }

        // If no value in source string, no value in translation
        if (!entityAST.value) {
          $('#ftl-area > .main-value').hide();
        }

        // Ignore editing for anonymous users
        if (!Pontoon.user.id) {
          $('#ftl-area input').prop('readonly', true);
        }

        Pontoon.fluent.focusFirstField();
        Pontoon.fluent.toggleEditorToolbar();

        Pontoon.moveCursorToBeginning();
        Pontoon.updateCurrentTranslationLength();
        Pontoon.updateInPlaceTranslation();

        return true;
      },


      /*
       * Is ast of a simple string?
       */
      isSimpleString: function (ast) {
        if (
          ast &&
          ast.value &&
          ast.value.elements.length === 1 &&
          ast.value.elements[0].type === 'TextElement'
        ) {
          return true;
        }

        return false;
      },


      /*
       * Serialize value with placeables into a simple string
       */
      serializePlaceables: function (elements) {
        var translatedValue = '';

        elements.forEach(function (item) {
          if (item.type === 'TextElement') {
            translatedValue += item.value;
          }
          else if (item.type === 'ExternalArgument') {
            translatedValue += '{$' + item.id.name + '}';
          }
          else if (item.type === 'MessageReference') {
            translatedValue += '{' + item.id.name + '}';
          }
        });

        return translatedValue;
      },


      /*
       * Generate input element with the given properties
       */
      inputValueElement: function (id, value, maxlength) {
        var base = '<input class="value" id="ftl-id-' + id + '" type="text" value="' + value + '"';

        if (typeof maxlength !== 'undefined' && maxlength !== null) {
          base += ' maxlength="' + maxlength + '"';
        }

        base += ' dir="' + Pontoon.locale.direction +
          '" data-script="' + Pontoon.locale.script +
          '" lang="' + Pontoon.locale.code + '">';
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

        var ast = fluentParser.parseEntry(entity.original);
        var original = '';

        $('#ftl-original section ul').empty();
        $('#original').hide();
        $('#ftl-original').show();

        // Plurals
        if (entity.isFTLplural) {
          var variants = ast.value.elements[0].variants;
          variants.forEach(function (item) {
            original += '<li>' +
              '<span class="id">' + (item.key.value || item.key.name) + '</span>' +
              '<span class="value">' + self.serializePlaceables(item.value.elements) +
              '</span>' +
            '</li>';
          });

        }
        else if (
          ast.value &&
          ast.value.elements.length === 1 &&
          ast.value.elements[0].type === 'TextElement'
        ) {
          original += '<li><p>' + self.serializePlaceables(ast.value.elements) + '</p></li>';
        }

        // Attributes
        if (ast.attributes && ast.attributes.length) {
          ast.attributes.forEach(function (attr) {
            $('#ftl-original .attributes ul')
              .append(
                '<li>' +
                  '<span class="id">' + attr.id.name + '</span>' +
                  '<span class="value">' + attr.value.elements[0].value + '</span>' +
                '</li>'
              );
          });
        }
        // Rich FTL string display does not support the translation: show source
        else if (original === '') {
          // Remove comment
          ast.comment = null;
          original = '<li class="source">' + fluentSerializer.serializeEntry(ast) + '</li>';
        }

        $('#ftl-original .main-value ul').append(original);
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
          var value = $('#ftl-area > .main-value input').val();
          var attributes = '';

          // Plurals
          if (entity.isFTLplural) {
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
              value = '{ $num ->' + value + '\n  }';
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
            return response;
          }

          var ast = fluentParser.parseEntry(source);

          if (ast.value) {
            response = this.serializePlaceables(ast.value.elements);
          }
          // Attributes
          else {
            var attributes = ast.attributes;
            if (attributes && attributes.length) {
              response = this.serializePlaceables(attributes[0].value.elements);
            }
          }

          // Plurals
          if (
            ast.value &&
            ast.value.elements &&
            ast.value.elements.length &&
            ast.value.elements[0].expression &&
            ast.value.elements[0].variants
          ) {
            var variants = ast.value.elements[0].variants;
            var isFTLplural = variants.every(function (element) {
              var key = element.key.name;
              var isPlural = Pontoon.CLDR_PLURALS.indexOf(key) !== -1;
              var isInteger = element.key.type === 'NumberExpression';

              return isPlural || isInteger;
            });

            if (isFTLplural) {
              response = this.serializePlaceables(variants[0].value.elements);
              entity.isFTLplural = true;
            }
          }
        }

        return response;
      },


      /*
       * Focus first field of the FTL editor
       */
      focusFirstField: function () {
        $('#ftl-area input.value:visible, #ftl-area textarea:visible').first().focus();
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

      var translated = (translation !== entity.key + ' = ');
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
        translation = entity.key + ' = ';
      }

      $('#translation').val(translation);
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
  $('#ftl-area .attributes').on('keyup', 'input:first', function () {
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

  // Select access key via input
  $('#ftl-area .attributes').on('keyup', '#ftl-id-accesskey', function () {
    var accesskey = $(this).val().toUpperCase();

    if (accesskey) {
      $('.accesskeys div').removeClass('active');
      $('.accesskeys div:contains("' + accesskey + '")').addClass('active');
    }
  });

});
