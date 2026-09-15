import { copyMessageEntry } from './copyMessageEntry';
import { parseEntry } from './parseEntry';
import { editMessageEntry } from './editMessageEntry';
import { serializeEntry } from './serializeEntry';

const plural = 'key = { $n ->\n    [one] ONE\n   *[other] OTHER\n    }';

function values(entry) {
  return editMessageEntry(entry).map((field) => field.handle.current.value);
}

describe('copyMessageEntry', () => {
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

  it('fills additional plural categories from the source catchall', () => {
    const source = parseEntry('fluent', plural);
    const result = copyMessageEntry(source, { code: 'ar' });
    expect(values(result)).toEqual([
      'OTHER',
      'ONE',
      'OTHER',
      'OTHER',
      'OTHER',
      'OTHER',
    ]);
    expect(serializeEntry(source)).toBe(
      serializeEntry(parseEntry('fluent', plural)),
    );
  });

  it('collapses a single-category locale to its catchall pattern', () => {
    const result = copyMessageEntry(parseEntry('fluent', plural), {
      code: 'zh',
    });
    expect(values(result)).toEqual(['OTHER']);
    expect(editMessageEntry(result)[0].keys).toEqual([]);
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
