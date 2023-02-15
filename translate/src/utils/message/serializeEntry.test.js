import { serializeEntry } from './serializeEntry';

describe('serializeEntry("simple", ...)', () => {
  it('serializes an empty value', () => {
    const entry = {
      id: 'key',
      value: { type: 'message', declarations: [], pattern: { body: [] } },
    };
    expect(serializeEntry('simple', entry)).toEqual('');
  });

  it('serializes a simple value', () => {
    const entry = {
      id: 'key',
      value: {
        type: 'message',
        declarations: [],
        pattern: { body: [{ type: 'text', value: 'foo' }] },
      },
    };
    expect(serializeEntry('simple', entry)).toEqual('foo');
  });

  it('serializes a value with multiple elements', () => {
    const entry = {
      id: 'key',
      value: {
        type: 'message',
        declarations: [],
        pattern: {
          body: [
            { type: 'text', value: 'foo' },
            { type: 'text', value: 'bar' },
          ],
        },
      },
    };
    expect(serializeEntry('simple', entry)).toEqual('foobar');
  });

  it('ignores attributes', () => {
    const entry = {
      id: 'key',
      value: {
        type: 'message',
        declarations: [],
        pattern: { body: [{ type: 'text', value: 'foo' }] },
      },
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
        pattern: {
          body: [
            { type: 'text', value: 'foo' },
            { type: 'literal', value: 'bar' },
          ],
        },
      },
    };
    expect(() => serializeEntry('simple', entry)).toThrow(
      /^Unsupported simple element type: literal/,
    );
  });
});
