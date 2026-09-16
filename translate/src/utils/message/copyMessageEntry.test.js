import { copyMessageEntry } from './copyMessageEntry';
import { parseEntry } from './parseEntry';
import { editMessageEntry } from './editMessageEntry';
import { serializeEntry } from './serializeEntry';

const plural = 'key = { $n ->\n    [one] ONE\n   *[other] OTHER\n    }';

function values(entry) {
  return editMessageEntry(entry).map((field) => field.handle.current.value);
}

describe('copyMessageEntry', () => {
  it.each(['ru', 'uk', 'pl', 'be', 'szl'])(
    'copies the source catchall into the %s default form',
    (code) => {
      const result = copyMessageEntry(parseEntry('fluent', plural), { code });
      expect(values(result)).toEqual(['ONE', '', 'OTHER']);
    },
  );

  it('keeps missing Slovenian categories empty while copying its catchall', () => {
    const result = copyMessageEntry(parseEntry('fluent', plural), {
      code: 'sl',
    });
    expect(values(result)).toEqual(['ONE', '', '', 'OTHER']);
  });

  it('uses a differently named source catchall when the selector collapses', () => {
    const source = parseEntry('fluent', plural.replace('*[other]', '*[many]'));
    expect(values(copyMessageEntry(source, { code: 'zh' }))).toEqual(['OTHER']);
  });

  it('keeps non-plural branches when a plural selector collapses', () => {
    const source = parseEntry(
      'fluent',
      [
        'key = { $n ->',
        '    [one] { PLATFORM() ->',
        '        [windows] ONE WINDOWS',
        '       *[other] ONE OTHER',
        '        }',
        '   *[other] { PLATFORM() ->',
        '        [windows] MANY WINDOWS',
        '       *[other] MANY OTHER',
        '        }',
        '    }',
      ].join('\n'),
    );
    const result = copyMessageEntry(source, { code: 'zh' });
    expect(values(result)).toEqual(['MANY WINDOWS', 'MANY OTHER']);
    expect(editMessageEntry(result).map((field) => field.keys.length)).toEqual([
      1, 1,
    ]);
  });

  it('leaves plural categories absent from the copied locale empty', () => {
    const source = parseEntry('fluent', plural);
    const result = copyMessageEntry(source, { code: 'ar' });
    expect(values(result)).toEqual(['', 'ONE', '', '', '', 'OTHER']);
    expect(serializeEntry(source)).toBe(
      serializeEntry(parseEntry('fluent', plural)),
    );
  });

  it('copies a plain translation into the default form without removing plurals', () => {
    const source = parseEntry('fluent', 'key = TRANSLATION');
    const original = parseEntry('fluent', plural);
    const result = copyMessageEntry(source, { code: 'en' }, original);
    expect(values(result)).toEqual(['', 'TRANSLATION']);
  });

  it('collapses a single-category locale to its catchall pattern', () => {
    const result = copyMessageEntry(parseEntry('fluent', plural), {
      code: 'zh',
    });
    expect(values(result)).toEqual(['OTHER']);
    expect(editMessageEntry(result)[0].keys).toEqual([]);
  });

  it('retains plural attributes and copied local attributes without mutating the template', () => {
    const original = parseEntry(
      'fluent',
      'key = VALUE\n    .label = { $n ->\n        [one] ONE\n       *[other] OTHER\n        }',
    );
    const before = serializeEntry(original);
    const copied = parseEntry(
      'fluent',
      'key = COPIED\n    .label = LABEL\n    .gender = feminine',
    );
    const result = copyMessageEntry(copied, { code: 'en' }, original);
    expect(values(result)).toEqual(['COPIED', '', 'LABEL', 'feminine']);
    expect(serializeEntry(original)).toBe(before);
  });

  it('preserves explicit numeric variants', () => {
    const source = parseEntry(
      'fluent',
      plural.replace('[one] ONE', '[0] ZERO\n    [one] ONE'),
    );
    const result = copyMessageEntry(source, { code: 'zh' });
    expect(values(result)).toEqual(['ZERO', 'OTHER']);
  });

  it('preserves non-plural selectors', () => {
    const source = parseEntry(
      'fluent',
      'key = { PLATFORM() ->\n    [windows] WINDOWS\n   *[other] OTHER\n    }',
    );
    expect(serializeEntry(copyMessageEntry(source, { code: 'zh' }))).toBe(
      serializeEntry(source),
    );
  });

  it('remaps attributes without discarding the value', () => {
    const source = parseEntry(
      'fluent',
      'key = VALUE\n    .label = { $n ->\n        [one] ONE\n       *[other] OTHER\n        }',
    );
    expect(values(copyMessageEntry(source, { code: 'zh' }))).toEqual([
      'VALUE',
      'OTHER',
    ]);
  });
});
