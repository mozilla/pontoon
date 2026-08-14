import { buildMessageEntry } from './buildMessageEntry';
import { getEmptyMessageEntry } from './getEmptyMessage';
import { parseEntry } from './parseEntry';

describe('buildMessageEntry', () => {
  it('matches getEmptyMessageEntry when value is empty', () => {
    const base = parseEntry(
      'android',
      'Hello, {$arg1 :string @source=|%1$s|}!',
    );
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: '' } } },
    ]);
    const empty = getEmptyMessageEntry(base, { code: 'en-US' });
    expect(result).toEqual(empty);
  });

  it('updates a plain entry', () => {
    const base = parseEntry('gettext', 'Hello World');
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: 'Bonjour Monde' } } },
    ]);
    expect(result).toEqual({
      format: 'gettext',
      id: '',
      value: ['Bonjour Monde'],
    });
  });

  it('updates an Android entry', () => {
    const base = parseEntry(
      'android',
      'Hello, {$arg1 :string @source=|%1$s|}!',
    );
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: 'Bonjour, %1$s !' } } },
    ]);
    expect(result).toEqual({
      format: 'android',
      id: '',
      value: [
        'Bonjour, ',
        { $: 'arg1', fn: 'string', attr: { source: '%1$s' } },
        ' !',
      ],
    });
  });

  it('updates an Xcode entry', () => {
    const base = parseEntry('xcode', 'Hello, {$arg @source=|%@|}!');
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: 'Bonjour, %@ !' } } },
    ]);
    expect(result).toEqual({
      format: 'xcode',
      id: '',
      value: ['Bonjour, ', { $: 'arg', attr: { source: '%@' } }, ' !'],
    });
  });

  it('updates a simple Fluent entry', () => {
    const base = parseEntry('fluent', 'msg = Hello { -world }\n');
    const result = buildMessageEntry(base, [
      {
        name: '',
        keys: [],
        handle: { current: { value: 'Bonjour {-world}' } },
      },
    ]);
    expect(result).toEqual({
      format: 'fluent',
      id: 'msg',
      value: ['Bonjour ', { _: '-world', fn: 'message' }],
    });
  });

  it('updates a complex Fluent entry', () => {
    const base = parseEntry(
      'fluent',
      'msg = { $n ->\n   [one] ONE\n  *[other] OTHER\n  }\n  .attr = ATTR\n',
    );
    const result = buildMessageEntry(base, [
      {
        name: '',
        keys: ['one'],
        handle: { current: { value: 'trans ONE' } },
      },
      {
        name: '',
        keys: [{ '*': 'other' }],
        handle: { current: { value: 'trans OTHER' } },
      },
      {
        name: 'attr',
        keys: [],
        handle: { current: { value: 'trans ATTR' } },
      },
    ]);
    expect(result).toEqual({
      format: 'fluent',
      id: 'msg',
      value: {
        decl: { n: { $: 'n', fn: 'number' } },
        sel: ['n'],
        alt: [
          { keys: ['one'], pat: ['trans ONE'] },
          { keys: [{ '*': 'other' }], pat: ['trans OTHER'] },
        ],
      },
      attributes: new Map([['attr', ['trans ATTR']]]),
    });
  });

  it('returns null on Fluent parse error', () => {
    const base = parseEntry('fluent', 'msg = Hello { -world }\n');
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: 'Hello {' } } },
    ]);
    expect(result).toBeNull();
  });

  it('returns null on Android parse error', () => {
    const base = parseEntry('android', 'Hello {$arg1 :string @source=|%1$s|}!');
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: 'Hello <a>' } } },
    ]);
    expect(result).toBeNull();
  });

  it('returns null on webext parse error', () => {
    const base = parseEntry('webext', 'Hello');
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: 'Hello $x$' } } },
    ]);
    expect(result).toBeNull();
  });

  it('returns null on Xcode parse error', () => {
    const base = parseEntry('xcode', 'Hello {$arg :string @source=|%@|}!');
    const result = buildMessageEntry(base, [
      { name: '', keys: [], handle: { current: { value: 'Hello <' } } },
    ]);
    expect(result).toBeNull();
  });

  it('keeps surrounding spaces by default', () => {
    const base = parseEntry('gettext', 'Hello World');
    const result = buildMessageEntry(base, [
      {
        name: '',
        keys: [],
        handle: { current: { value: ' Bonjour Monde\t ' } },
      },
    ]);
    expect(result).toEqual({
      format: 'gettext',
      id: '',
      value: [' Bonjour Monde\t '],
    });
  });

  it('trims surrounding spaces with options.trim', () => {
    const base = parseEntry('gettext', 'Hello World');
    const result = buildMessageEntry(
      base,
      [
        {
          name: '',
          keys: [],
          handle: { current: { value: ' Bonjour Monde\t ' } },
        },
      ],
      { trim: true },
    );
    expect(result).toEqual({
      format: 'gettext',
      id: '',
      value: ['Bonjour Monde'],
    });
  });
});
