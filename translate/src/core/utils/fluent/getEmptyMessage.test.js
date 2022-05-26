import ftl from '@fluent/dedent';
import { getEmptyMessage } from './getEmptyMessage';
import { parseEntry } from './parser';
import { serializeEntry } from './serializer';

const LOCALE = {
  code: 'sl',
  cldrPlurals: [1, 2, 3, 5],
};

const emptyValue = {
  type: 'Pattern',
  elements: [{ type: 'TextElement', value: '' }],
};
const emptyVariant = (name) => ({
  type: 'Variant',
  key: { type: 'Identifier', name },
  value: emptyValue,
  default: false,
});

describe('getEmptyMessage', () => {
  it('empties a simple value', () => {
    const source = parseEntry('my-message = Some value');
    const message = getEmptyMessage(source, LOCALE);

    expect(message.value.elements[0].value).toEqual('');
    expect(message.value.elements).toHaveLength(1);
  });

  it('empties a value with multiple elements', () => {
    const source = parseEntry('my-message = Hello { $small } World');
    const message = getEmptyMessage(source, LOCALE);

    expect(message.value.elements[0].value).toEqual('');
    expect(message.value.elements).toHaveLength(1);
  });

  it('empties a single simple attribute', () => {
    const source = parseEntry('my-message =\n    .my-attr = Hello');
    const message = getEmptyMessage(source, LOCALE);

    expect(message.attributes[0].id.name).toEqual('my-attr');

    expect(message.attributes[0].value.elements[0].value).toEqual('');
    expect(message.attributes[0].value.elements).toHaveLength(1);
  });

  it('empties both value and attributes', () => {
    const source = parseEntry('my-message = Some value\n    .my-attr = Hello');
    const message = getEmptyMessage(source, LOCALE);

    expect(message).toEqual({
      type: 'Message',
      id: { type: 'Identifier', name: 'my-message' },
      value: {
        type: 'Pattern',
        elements: [{ type: 'TextElement', value: '' }],
      },
      attributes: [
        {
          type: 'Attribute',
          id: { type: 'Identifier', name: 'my-attr' },
          value: {
            type: 'Pattern',
            elements: [{ type: 'TextElement', value: '' }],
          },
        },
      ],
      comment: null,
    });

    const str = serializeEntry(message);
    expect(str).toBe(ftl`
      my-message = { "" }
          .my-attr = { "" }

      `);
  });

  it('empties message with no value and several attributes', () => {
    const source = parseEntry(
      'my-message =\n    .my-attr = Hello\n    .title = Title',
    );
    const message = getEmptyMessage(source, LOCALE);

    expect(message.attributes).toEqual([
      {
        type: 'Attribute',
        id: { type: 'Identifier', name: 'my-attr' },
        value: emptyValue,
      },
      {
        type: 'Attribute',
        id: { type: 'Identifier', name: 'title' },
        value: emptyValue,
      },
    ]);

    const str = serializeEntry(message);
    expect(str).toBe(ftl`
      my-message =
          .my-attr = { "" }
          .title = { "" }

      `);
  });

  it('empties a select expression', () => {
    const input = `
my-entry =
    { PLATFORM() ->
        [variant] Hello!
       *[another-variant] { reference } World!
    }`;
    const source = parseEntry(input);
    const message = getEmptyMessage(source, LOCALE);

    expect(message.value.elements[0].expression.variants).toEqual([
      emptyVariant('variant'),
      { ...emptyVariant('another-variant'), default: true },
    ]);

    const str = serializeEntry(message);
    expect(str).toBe(ftl`
      my-entry =
          { PLATFORM() ->
              [variant] { "" }
             *[another-variant] { "" }
          }

      `);
  });

  it('empties custom plural variants and creates empty default locale plural variants', () => {
    const input = `
my-entry =
    { $num ->
        [0] Yo!
        [one] Hello!
       *[other] { reference } World!
    }`;
    const source = parseEntry(input);
    const message = getEmptyMessage(source, LOCALE);

    expect(message.value.elements[0].expression.variants).toEqual([
      {
        type: 'Variant',
        key: { type: 'NumberLiteral', value: '0' },
        value: emptyValue,
        default: false,
      },
      emptyVariant('one'),
      emptyVariant('two'),
      emptyVariant('few'),
      { ...emptyVariant('other'), default: true },
    ]);

    const str = serializeEntry(message);
    expect(str).toBe(ftl`
      my-entry =
          { $num ->
              [0] { "" }
              [one] { "" }
              [two] { "" }
              [few] { "" }
             *[other] { "" }
          }

      `);
  });

  it('handles messages with multiple selectors correctly', () => {
    const input = ftl`
      selector-multi =
        There { $num ->
            [one] is one email
           *[other] are many emails
        } for { $gender ->
           *[masculine] him
            [feminine] her
        }
      `;
    const source = parseEntry(input);
    const message = getEmptyMessage(source, LOCALE);
    const str = serializeEntry(message);
    expect(str).toBe(ftl`
      selector-multi =
          { $num ->
              [one] { "" }
              [two] { "" }
              [few] { "" }
             *[other] { "" }
          } { $gender ->
             *[masculine] { "" }
              [feminine] { "" }
          }

      `);
  });
});
