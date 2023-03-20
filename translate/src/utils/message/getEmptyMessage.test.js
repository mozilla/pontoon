import ftl from '@fluent/dedent';
import { getEmptyMessageEntry } from './getEmptyMessage';
import { parseEntry } from './parseEntry';
import { serializeEntry } from './serializeEntry';

const LOCALE = { code: 'sl' };

describe('getEmptyMessage', () => {
  it('empties a simple value', () => {
    const source = parseEntry('my-message = Some value');
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry('ftl', entry)).toEqual('my-message = { "" }\n');
  });

  it('empties a value with multiple elements', () => {
    const source = parseEntry('my-message = Hello { $small } World');
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry('ftl', entry)).toEqual('my-message = { "" }\n');
  });

  it('empties a single simple attribute', () => {
    const source = parseEntry('my-message =\n    .my-attr = Hello');
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry('ftl', entry)).toEqual(
      'my-message =\n    .my-attr = { "" }\n',
    );
  });

  it('empties both value and attributes', () => {
    const source = parseEntry('my-message = Some value\n    .my-attr = Hello');
    const entry = getEmptyMessageEntry(source, LOCALE);

    expect(serializeEntry('ftl', entry)).toBe(ftl`
      my-message = { "" }
          .my-attr = { "" }

      `);
  });

  it('empties message with no value and several attributes', () => {
    const source = parseEntry(ftl`
      my-message =
          .my-attr = Hello
          .title = Title
      `);
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry('ftl', entry)).toBe(ftl`
      my-message =
          .my-attr = { "" }
          .title = { "" }

      `);
  });

  it('empties a select expression', () => {
    const source = parseEntry(ftl`
      my-entry =
          { PLATFORM() ->
              [variant] Hello!
             *[another-variant] { reference } World!
          }
      `);
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry('ftl', entry)).toBe(ftl`
      my-entry =
          { PLATFORM() ->
              [variant] { "" }
             *[another-variant] { "" }
          }

      `);
  });

  it('empties custom plural variants and creates empty default locale plural variants', () => {
    const source = parseEntry(ftl`
      my-entry =
          { $num ->
              [0] Yo!
              [one] Hello!
             *[other] { reference } World!
          }

      `);
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry('ftl', entry)).toBe(ftl`
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
    const source = parseEntry(ftl`
      selector-multi =
        There { $num ->
            [one] is one email
           *[other] are many emails
        } for { $gender ->
           *[masculine] him
            [feminine] her
        }
      `);
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry('ftl', entry)).toBe(ftl`
      selector-multi =
          { $num ->
              [one]
                  { $gender ->
                      [feminine] { "" }
                     *[masculine] { "" }
                  }
              [two]
                  { $gender ->
                      [feminine] { "" }
                     *[masculine] { "" }
                  }
              [few]
                  { $gender ->
                      [feminine] { "" }
                     *[masculine] { "" }
                  }
             *[other]
                  { $gender ->
                      [feminine] { "" }
                     *[masculine] { "" }
                  }
          }

      `);
  });

  it('handles plural messages for locales with no plurals', () => {
    const source = parseEntry(ftl`
      selector-multi =
        { $num ->
            [one] ONE
           *[other] OTHER
        }
      `);
    const entry = getEmptyMessageEntry(source, { code: 'zh' });
    expect(serializeEntry('ftl', entry)).toBe(ftl`
      selector-multi = { "" }

      `);
  });

  it('handles plural messages for special locales', () => {
    const source = parseEntry(ftl`
      selector-multi =
        { $num ->
            [one] ONE
           *[other] OTHER
        }
      `);
    const entry = getEmptyMessageEntry(source, { code: 'pl' });
    expect(serializeEntry('ftl', entry)).toBe(ftl`
      selector-multi =
          { $num ->
              [one] { "" }
              [few] { "" }
             *[many] { "" }
          }

      `);
  });
});
