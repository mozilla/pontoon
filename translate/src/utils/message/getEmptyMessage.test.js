import ftl from '@fluent/dedent';
import { getEmptyMessageEntry } from './getEmptyMessage';
import { parseEntry } from './parseEntry';
import { serializeEntry } from './serializeEntry';

const LOCALE = { code: 'sl' };

describe('getEmptyMessage', () => {
  it('empties a simple value', () => {
    const source = parseEntry('fluent', 'my-message = Some value');
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry(entry)).toEqual('my-message = { "" }\n');
  });

  it('empties a value with multiple elements', () => {
    const source = parseEntry('fluent', 'my-message = Hello { $small } World');
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry(entry)).toEqual('my-message = { "" }\n');
  });

  it('empties a single simple attribute', () => {
    const source = parseEntry('fluent', 'my-message =\n    .my-attr = Hello');
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry(entry)).toEqual(
      'my-message =\n    .my-attr = { "" }\n',
    );
  });

  it('empties both value and attributes', () => {
    const source = parseEntry(
      'fluent',
      'my-message = Some value\n    .my-attr = Hello',
    );
    const entry = getEmptyMessageEntry(source, LOCALE);

    expect(serializeEntry(entry)).toBe(ftl`
      my-message = { "" }
          .my-attr = { "" }

      `);
  });

  it('empties message with no value and several attributes', () => {
    const source = parseEntry(
      'fluent',
      ftl`
      my-message =
          .my-attr = Hello
          .title = Title
      `,
    );
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry(entry)).toBe(ftl`
      my-message =
          .my-attr = { "" }
          .title = { "" }

      `);
  });

  it('empties a select expression', () => {
    const source = parseEntry(
      'fluent',
      ftl`
      my-entry =
          { PLATFORM() ->
              [variant] Hello!
             *[another-variant] { reference } World!
          }
      `,
    );
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry(entry)).toBe(ftl`
      my-entry =
          { PLATFORM() ->
              [variant] { "" }
             *[another-variant] { "" }
          }

      `);
  });

  it('empties custom plural variants and creates empty default locale plural variants', () => {
    const source = parseEntry(
      'fluent',
      ftl`
      my-entry =
          { $num ->
              [0] Yo!
              [one] Hello!
             *[other] { reference } World!
          }

      `,
    );
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry(entry)).toBe(ftl`
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
    const source = parseEntry(
      'fluent',
      ftl`
      selector-multi =
        There { $num ->
            [one] is one email
           *[other] are many emails
        } for { $gender ->
           *[masculine] him
            [feminine] her
        }
      `,
    );
    const entry = getEmptyMessageEntry(source, LOCALE);
    expect(serializeEntry(entry)).toBe(ftl`
      selector-multi =
          { $num ->
              [one]
                  { $gender ->
                     *[masculine] { "" }
                      [feminine] { "" }
                  }
              [two]
                  { $gender ->
                     *[masculine] { "" }
                      [feminine] { "" }
                  }
              [few]
                  { $gender ->
                     *[masculine] { "" }
                      [feminine] { "" }
                  }
             *[other]
                  { $gender ->
                     *[masculine] { "" }
                      [feminine] { "" }
                  }
          }

      `);
  });

  it('handles plural messages for locales with no plurals', () => {
    const source = parseEntry(
      'fluent',
      ftl`
      selector-multi =
        { $num ->
            [one] ONE
           *[other] OTHER
        }
      `,
    );
    const entry = getEmptyMessageEntry(source, { code: 'zh' });
    expect(serializeEntry(entry)).toBe(ftl`
      selector-multi = { "" }

      `);
  });

  for (const code of ['fr', 'fr-BE', 'ca-valencia']) {
    it(`handles plural messages for Romance locales (${code})`, () => {
      const source = parseEntry(
        'fluent',
        ftl`
      selector-multi =
        { $num ->
            [one] ONE
           *[other] OTHER
        }
      `,
      );
      const entry = getEmptyMessageEntry(source, { code });
      expect(serializeEntry('fluent', entry)).toBe(ftl`
      selector-multi =
          { $num ->
              [one] { "" }
             *[other] { "" }
          }

      `);
    });
  }

  it('handles plural messages for Slavic locales', () => {
    const source = parseEntry(
      'fluent',
      ftl`
      selector-multi =
        { $num ->
            [one] ONE
           *[other] OTHER
        }
      `,
    );
    const entry = getEmptyMessageEntry(source, { code: 'pl' });
    expect(serializeEntry(entry)).toBe(ftl`
      selector-multi =
          { $num ->
              [one] { "" }
              [few] { "" }
             *[many] { "" }
          }

      `);
  });
});
