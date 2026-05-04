import { buildMessageEntry } from './buildMessageEntry';
import { getEmptyMessageEntry } from './getEmptyMessage';
import { getPlaceholderMap } from './placeholders';
import { parseEntry } from './parseEntry';
import { serializeEntry } from './serializeEntry';

const LOCALE = { code: 'en-US' };

describe('buildMessageEntry', () => {
  it('matches getEmptyMessageEntry when value is empty and placeholders map is non-empty', () => {
    const base = parseEntry(
      'android',
      'Hello, {$arg1 :string @source=|%1$s|}!',
    );
    const placeholders = getPlaceholderMap(base.value);
    expect(placeholders).not.toBeNull();

    const result = buildMessageEntry(base, placeholders, [
      { name: '', keys: [], value: '' },
    ]);
    const empty = getEmptyMessageEntry(base, LOCALE);

    expect(result).toEqual(empty);
  });

  it('replaces a placeholder in a non-empty value', () => {
    const base = parseEntry(
      'android',
      'Hello, {$arg1 :string @source=|%1$s|}!',
    );
    const placeholders = getPlaceholderMap(base.value);

    const result = buildMessageEntry(base, placeholders, [
      { name: '', keys: [], value: 'Bonjour, %1$s!' },
    ]);

    expect(serializeEntry(result)).toEqual(
      'Bonjour, {$arg1 :string @source=|%1$s|}!',
    );
  });

  it('matches getEmptyMessageEntry when value is empty and placeholders map is null', () => {
    const base = parseEntry('fluent', 'msg = Hello World\n');
    expect(base).not.toBeNull();

    const result = buildMessageEntry(base, null, [
      { name: '', keys: [], value: '' },
    ]);
    const empty = getEmptyMessageEntry(base, LOCALE);

    expect(result).toEqual(empty);
  });

  it('sets a simple value without placeholders', () => {
    const base = parseEntry('android', 'Hello World');

    const result = buildMessageEntry(base, null, [
      { name: '', keys: [], value: 'Bonjour Monde' },
    ]);

    expect(serializeEntry(result)).toEqual('Bonjour Monde');
  });
});
