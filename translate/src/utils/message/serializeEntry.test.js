import ftl from '@fluent/dedent';

import { serializeEntry } from './serializeEntry';

describe('serialize fluent entry', () => {
  it('serialises a Fluent message with selectors', () => {
    const entry = {
      format: 'fluent',
      id: 'my-entry',
      value: {
        decl: {
          num: { $: 'num', fn: 'number' },
          gender: { $: 'gender', fn: 'string' },
        },
        sel: ['num', 'gender'],
        alt: [
          {
            keys: ['one', { '*': 'masculine' }],
            pat: ['There is one email for { $awesome } him'],
          },
          {
            keys: ['one', 'feminine'],
            pat: ['There is one email for { $awesome } her'],
          },
          {
            keys: [{ '*': 'other' }, { '*': 'masculine' }],
            pat: ['There are { $num } emails for { $awesome } him'],
          },
          {
            keys: [{ '*': 'other' }, 'feminine'],
            pat: ['There are { $num } emails for { $awesome } her'],
          },
        ],
      },
    };
    expect(serializeEntry(entry)).toEqual(ftl`
      my-entry =
          { $num ->
              [one]
                  { $gender ->
                     *[masculine] There is one email for { $awesome } him
                      [feminine] There is one email for { $awesome } her
                  }
             *[other]
                  { $gender ->
                     *[masculine] There are { $num } emails for { $awesome } him
                      [feminine] There are { $num } emails for { $awesome } her
                  }
          }

      `);
  });
});

describe('serialize plain entry', () => {
  it('serialises an empty value', () => {
    const entry = { format: 'plain', id: 'key', value: [] };
    expect(serializeEntry(entry)).toEqual('');
  });

  it('serialises a plain value', () => {
    const entry = { format: 'plain', id: 'key', value: ['foo'] };
    expect(serializeEntry(entry)).toEqual('foo');
  });

  it('serialises a value with multiple elements', () => {
    const entry = { format: 'plain', id: 'key', value: ['foo', 'bar'] };
    expect(serializeEntry(entry)).toEqual('foobar');
  });

  it('ignores attributes', () => {
    const entry = {
      format: 'plain',
      id: 'key',
      value: ['foo'],
      attributes: new Map([['key', { type: 'junk' }]]),
    };
    expect(serializeEntry(entry)).toEqual('foo');
  });

  it('complains about missing value', () => {
    const entry = { format: 'plain', id: 'key' };
    expect(() => serializeEntry(entry)).toThrow(/^Unsupported plain message/);
  });

  it('complains about junk', () => {
    const entry = { format: 'plain', id: 'key', value: { type: 'junk' } };
    expect(() => serializeEntry(entry)).toThrow(/^Unsupported plain message/);
  });

  it('complains about non-array values', () => {
    const entry = { format: 'plain', id: 'key', value: {} };
    expect(() => serializeEntry(entry)).toThrow(/^Unsupported plain message/);
  });

  it('complains about non-text pattern elements', () => {
    const entry = { format: 'plain', id: 'key', value: ['foo', { _: 'bar' }] };
    expect(() => serializeEntry(entry)).toThrow(/Unsupported pattern part/);
  });
});
