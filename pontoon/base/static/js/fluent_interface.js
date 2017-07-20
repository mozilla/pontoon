/* Public functions used across different files */
var Pontoon = (function (my) {
  const fluentParser = new FluentSyntax.FluentParser({ withSpans: false });
  const fluentSerializer = new FluentSyntax.FluentSerializer();

  return $.extend(true, my, {
    fluent: {

      /*
       * Populate FTL translation area with existing data
       */
      renderEditor: function (translation) {
        $('#ftl-area > .main-value').show().find('input').val('');
        $('#ftl-area .attributes ul:first').empty();
        $('#ftl-area > .main-value ul li:not(":first")').remove();

        var self = this,
            entity = Pontoon.getEditorEntity(),
            isFTLplural = entity.isFTLplural,
            translation = translation || entity.translation[0],
            isTranslated = translation.pk,
            entity_ast = fluentParser.parseEntry(entity.original),
            entityAttributes = [],
            id, value;

        var attributes = entity_ast.attributes;
        if (isTranslated) {
          var translation_ast = fluentParser.parseEntry(translation.string);
          attributes = translation_ast.attributes;
        }

        if (entity_ast.attributes) {
          entityAttributes = $.map(entity_ast.attributes, function(item) {
            return item.id.name;
          });
        }

        // Plurals
        if (isFTLplural) {
          var pluralForms = $(Pontoon.locale.cldr_plurals).map(
            function() {
              return Pontoon.CLDR_PLURALS[this];
            }
          ).get();

          $.each(pluralForms, function(i) {
            var example = i === 3 ? 5 : i+1,
                value = isTranslated ? self.serializePlaceables(translation_ast.value.elements[0].variants[i].value.elements) : '';
            $('#ftl-area .main-value ul')
              .append(
                '<li class="clearfix">' +
                  '<label class="id built-in" for="ftl-id-' + this + '">' +
                    '<span>' + this + ' (e.g. </span><span class="stress">' + example + '</span>)<sub class="fa fa-remove remove" title="Remove"></sub>' +
                  '</label>' +
                  '<input class="value" id="ftl-id-' + this + '" type="text" value="' + value + '">' +
                '</li>');
          });

          $('#entity-value').parents('li').hide();
        }

        // Attributes
        if (!(attributes && attributes.length)) {
          return;
        }

        $.each(attributes, function() {
          id = this.id.name;
          value = isTranslated ? this.value.elements[0].value : '';

          var maxlength = label = input = cls = '';

          if (id === 'accesskey') {
            maxlength = '1';
            input = '<div class="accesskeys"></div>';
          }
          input += '<input class="value" id="ftl-id-' + id + '" type="text" value="' + value + '" maxlength="' + maxlength + '">';

          if ($.inArray(id, [entityAttributes])) {
            label = '<label class="id" for="ftl-id-' + id + '">' +
              '<span>' + id + '</span>' +
            '</label>';

          } else {
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
              '</li>');
        });

        // Update access keys presentaion
        $('#ftl-area .attributes input').keyup();

        // If no value in source string, no value in translation
        if (!entity_ast.value) {
          $('#ftl-area > .main-value').hide();
        }

        // Ignore editing for anonymous users
        if (!Pontoon.user.id) {
          $('#ftl-area input').prop('readonly', true);
        }
      },


      /*
       * Serialize value with placeables into a simple strings
       */
      serializePlaceables: function (elements) {
        var translatedValue = '';

        $.each(elements, function(i) {
          if (this.type === 'TextElement') {
            translatedValue += this.value;
          } else if (this.type === 'ExternalArgument') {
            translatedValue += ('{$' + this.id.name + '}');
          } else if (this.type === 'MessageReference') {
            translatedValue += ('{' + this.id.name + '}');
          }
        });

        return translatedValue;
      },


      /*
       * Toggle FTL button
       */
      toggleButton: function () {
        var entity = Pontoon.getEditorEntity();
        $('#ftl').toggle(entity.format === 'ftl');
      },


      /*
       * Toggle between standard and FTL translation editor
       */
      toggleEditor: function (activate) {
        if (activate) {
          $('#ftl-area').show();
          // TODO: Uncomment once attributes are fully supported (defaults, removing, validation)
          // $('#add-attribute').show();
          $('#translation-length, #copy').hide();

          $('#editor textarea').hide();
          $('#ftl').addClass('active');

          this.renderEditor();
          $('#ftl-area input.value:visible:first').focus();

        } else {
          $('#ftl-area').hide();
          // TODO: Uncomment once attributes are fully supported (defaults, removing, validation)
          // $('#add-attribute').hide();
          $('#translation-length, #copy').show();

          $('#editor textarea').show().focus();
          $('#ftl').removeClass('active');
        }

        Pontoon.moveCursorToBeginning();
      },


      /*
       * Toggle between standard and FTL original string
       */
      toggleOriginal: function () {
        var self = this,
            entity = Pontoon.getEditorEntity();

        if (entity.format !== 'ftl') {
          return;
        }

        var ast = fluentParser.parseEntry(entity.original),
            original = '';

        function renderOriginal(obj) {
          if (entity.isFTLplural) {
            var variants = ast.value.elements[0].variants;
            $.each(variants, function() {
              original += '<li><span class="id">' + (this.key.value || this.key.name) + '</span><span class="value">';
              original += self.serializePlaceables(this.value.elements);
              original += '</span></li>';
            });

          } else if (obj.attributes) {
            var id, value;
            $.each(obj.attributes, function() {
              id = this.id.name;
              value = this.value.elements[0].value;

              $('#ftl-original .attributes ul')
                .append(
                  '<li>' +
                    '<span class="id">' + id + '</span>' +
                    '<span class="value">' + value + '</span>' +
                  '</li>');
            });
          }
        }

        $('#ftl-original section ul').empty();

        if (entity.isComplexFTL) {
          $('#original').hide();
          $('#ftl-original').show();

          renderOriginal(ast);
          $('#ftl-original .main-value ul').append(original);

        } else {
          $('#original').show();
          $('#ftl-original').hide();
        }
      },


      /*
       * Get AST and any errors for the entity's translation
       */
      serializeTranslation: function(entity, translation) {
        if (entity.format !== 'ftl') {
          return translation;
        }

        if ($('#ftl').is('.active')) {
          // Main value
          var value = $('#ftl-area > .main-value input').val(),
              attributes = '';

          // Plurals
          if (entity.isFTLplural) {
            value = '{ ' + '$num ->';
            var variants = $('#ftl-area .main-value li:visible');

            variants.each(function(i) {
              var id = $(this).find('.id span:first').html().split(' ')[0],
                  val = $(this).find('.value').val(),
                  def = (i === (variants.length - 1)) ? '*' : '';

              if (id && val) {
                value += '\n  ' + def + '[' + id + '] ' + val;
              }
            });

            value += '\n  }';
          }

          // Attributes
          $('#ftl-area .attributes ul:first li').each(function() {
            var id = $(this).find('.id span').html() || $(this).find('.id').val(),
                val = $(this).find('.value').val();

            if (id && val) {
              attributes += '\n  .' + id + ' = ' + val;
            }
          });

          translation = (value ? ' = ' + value : '') + (attributes || '');

        // Mark multiline strings with indent
        } else if (translation.indexOf('\n') !== -1) {
          translation = ' = \n  ' + translation.replace(/\n/g, '\n  ');

        // Simple strings
        } else {
          translation = ' = ' + translation;
        }

        var content = entity.key + translation;
        return fluentSerializer.serializeEntry(fluentParser.parseEntry(content));
      },


      /*
       * Get simplified preview of the FTL object
       */
      getSimplePreview: function(object, fallback, entity) {
        var response = fallback;

        if (entity.format === 'ftl') {
          // Transfrom complex FTL-based strings into single-value strings
          var source = object.original || object.string;

          if (!source) {
            return response;
          }

          ast = fluentParser.parseEntry(source);

          if (ast.value) {
            response = this.serializePlaceables(ast.value.elements);

          // Attributes
          } else {
            var attributes = ast.attributes;
            if (attributes && attributes.length) {
              response = attributes[0].value.elements[0].value;
            }
          }

          // Plurals
          if (ast.value && ast.value.elements && ast.value.elements.length && ast.value.elements[0].expression && ast.value.elements[0].variants) {
            var variants = ast.value.elements[0].variants,
                isFTLplural = variants.every(function(element) {
                  var key = element.key.name,
                      isPlural = Pontoon.CLDR_PLURALS.indexOf(key) !== -1,
                      isInteger = element.key.type === 'NumberExpression';

                  return isPlural || isInteger;
                });

            if (isFTLplural) {
              response = variants[0].value.elements[0].value;
              entity.isFTLplural = true;
            }
          }

          // Mark complex strings
          if (ast.attributes && ast.attributes.length || (ast.value && ast.value.elements && ast.value.elements.length && ast.value.elements[0].expression && ast.value.elements[0].variants.length > 1)) {
            object.isComplexFTL = true;

          // Update entity and translation objects
          } else {
            if (object.hasOwnProperty('original')) {
              object.original = response;
              response = object.marked = Pontoon.doNotRender(response);
            } else if (object.hasOwnProperty('string')) {
              object.string = response;
            }
          }
        }

        return response;
      }

    }
  });
}(Pontoon || {}));

$(function() {

  // Ignore editing for anonymous users
  if (!Pontoon.user.id) {
    return;
  }

  // Toggle FTL mode
  $('#ftl').click(function (e) {
    e.preventDefault();
    Pontoon.fluent.toggleEditor(!$(this).is('.active'));
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
  $('#ftl-area .attributes').on('keyup', 'input:first', function() {
    var active = $('.accesskeys').find('.active').html(),
        unique = $(this).val().toUpperCase().split('').filter(function(item, i, ar) {
          return ar.indexOf(item) === i;
        });

    $('.accesskeys').empty();

    $.each(unique, function(i, v) {
      $('.accesskeys').append('<div' + ((v === active) ? ' class="active"' : '') + '>' + v + '</div>');
    });
  });

  // Select access key via click
  $('#ftl-area .attributes').on('click', '.accesskeys div', function() {
    var selected = $(this).is('.active');
    $('.accesskeys div').removeClass('active');

    if (!selected) {
      $(this).addClass('active');
    }

    $('#ftl-id-accesskey').val($('.accesskeys div.active').html());
  });

  // Select access key via input
  $('#ftl-area .attributes').on('keyup', '#ftl-id-accesskey', function() {
    var accesskey = $(this).val().toUpperCase();

    if (accesskey) {
      $('.accesskeys div').removeClass('active');
      $('.accesskeys div:contains("' + accesskey + '")').addClass('active');
    }
  });

  // Clear translation area
  $('#clear').click(function (e) {
    e.preventDefault();

    if ($('#ftl').is('.active')) {
      var translation = {
        pk: null,
        string: ''
      };

      Pontoon.fluent.renderEditor(translation);
      $('#ftl-area input.value:visible:first').focus();
    }
  });

  // Copy helpers result to translation
  $('#helpers section').on('click', 'li:not(".disabled")', function (e) {
    if ($('#ftl').is('.active')) {
      e.preventDefault();

      var translation = {
        pk: $(this).data('id'),
        string: this.string
      };

      $('#translation').val(''); // Invalidate main copy from helpers action
      Pontoon.fluent.renderEditor(translation);
      $('#ftl-area input.value:visible:first').focus();
    }
  });

});
