import ftl from '@fluent/dedent';

import { serializeEntry } from './serializeEntry';

describe('serializeEntry("fluent", ...)', () => {
  it('serialises a Fluent message with selectors', () => {
    const entry = {
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
    expect(serializeEntry('fluent', entry)).toEqual(ftl`
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

describe('serializeEntry("simple", ...)', () => {
  it('serialises an empty value', () => {
    const entry = { id: 'key', value: [] };
    expect(serializeEntry('simple', entry)).toEqual('');
  });

  it('serialises a plain value', () => {
    const entry = { id: 'key', value: ['foo'] };
    expect(serializeEntry('simple', entry)).toEqual('foo');
  });

  it('serialises a value with multiple elements', () => {
    const entry = { id: 'key', value: ['foo', 'bar'] };
    expect(serializeEntry('simple', entry)).toEqual('foobar');
  });

  it('ignores attributes', () => {
    const entry = {
      id: 'key',
      value: ['foo'],
      attributes: new Map([['key', { type: 'junk' }]]),
    };
    expect(serializeEntry('simple', entry)).toEqual('foo');
  });

  it('complains about missing value', () => {
    const entry = { id: 'key' };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple message/,
    );
  });

  it('complains about junk', () => {
    const entry = { id: 'key', value: { type: 'junk' } };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple message/,
    );
  });

  it('complains about non-array values', () => {
    const entry = { id: 'key', value: {} };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple message/,
    );
  });

  it('complains about non-text pattern elements', () => {
    const entry = { id: 'key', value: ['foo', { _: 'bar' }] };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /Unsupported pattern part/,
    );
  });
});
