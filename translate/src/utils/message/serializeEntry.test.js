import ftl from '@fluent/dedent';

import { serializeEntry } from './serializeEntry';

describe('serializeEntry("simple", ...)', () => {
  it('serializes an empty value', () => {
    const entry = {
      id: 'key',
      value: { type: 'message', declarations: [], pattern: [] },
    };
    expect(serializeEntry('simple', entry)).toEqual('');
  });

  it('serializes a simple value', () => {
    const entry = {
      id: 'key',
      value: { type: 'message', declarations: [], pattern: ['foo'] },
    };
    expect(serializeEntry('simple', entry)).toEqual('foo');
  });

  it('serializes a value with multiple elements', () => {
    const entry = {
      id: 'key',
      value: {
        type: 'message',
        declarations: [],
        pattern: ['foo', 'bar'],
      },
    };
    expect(serializeEntry('simple', entry)).toEqual('foobar');
  });

  it('serialises a Fluent message with selectors', () => {
    const entry = {
      id: 'my-entry',
      value: {
        type: 'select',
        declarations: [
          {
            type: 'input',
            name: 'num',
            value: {
              type: 'expression',
              arg: { type: 'variable', name: 'num' },
              functionRef: { type: 'function', name: 'number' },
            },
          },
          {
            type: 'input',
            name: 'gender',
            value: {
              type: 'expression',
              arg: { type: 'variable', name: 'gender' },
              functionRef: { type: 'function', name: 'string' },
            },
          },
        ],
        selectors: [
          { type: 'variable', name: 'num' },
          { type: 'variable', name: 'gender' },
        ],
        variants: [
          {
            keys: [
              { type: 'literal', value: 'one' },
              { type: '*', value: 'masculine' },
            ],
            value: ['There is one email for { $awesome } him'],
          },
          {
            keys: [
              { type: 'literal', value: 'one' },
              { type: 'literal', value: 'feminine' },
            ],
            value: ['There is one email for { $awesome } her'],
          },
          {
            keys: [
              { type: '*', value: 'other' },
              { type: '*', value: 'masculine' },
            ],
            value: ['There are { $num } emails for { $awesome } him'],
          },
          {
            keys: [
              { type: '*', value: 'other' },
              { type: 'literal', value: 'feminine' },
            ],
            value: ['There are { $num } emails for { $awesome } her'],
          },
        ],
      },
    };
    expect(serializeEntry('ftl', entry)).toEqual(ftl`
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

  it('ignores attributes', () => {
    const entry = {
      id: 'key',
      value: { type: 'message', declarations: [], pattern: ['foo'] },
      attributes: new Map([['key', { type: 'junk' }]]),
    };
    expect(serializeEntry('simple', entry)).toEqual('foo');
  });

  it('complains about missing value', () => {
    const entry = { id: 'key' };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple message type: undefined/,
    );
  });

  it('complains about junk', () => {
    const entry = { id: 'key', value: { type: 'junk' } };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple message type: junk/,
    );
  });

  it('complains about select', () => {
    const entry = { id: 'key', value: { type: 'select' } };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple message type: select/,
    );
  });

  it('complains about non-text pattern elements', () => {
    const entry = {
      id: 'key',
      value: {
        type: 'message',
        declarations: [],
        pattern: ['foo', { type: 'expression', arg: 'bar' }],
      },
    };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple element type: expression/,
    );
  });
});
