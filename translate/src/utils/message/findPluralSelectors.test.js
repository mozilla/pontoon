import ftl from '@fluent/dedent';
import { findPluralSelectors } from './findPluralSelectors';
import { parseEntry } from './parseEntry';

describe('findPluralSelectors', () => {
  it('returns [] for non-select messages', () => {
    const input = 'my-entry = Hello!';
    const entry = parseEntry(input);
    expect(findPluralSelectors(entry.value)).toMatchObject([]);
  });

  it('returns [0] if all variant keys are CLDR plurals', () => {
    const input = ftl`
      my-entry =
          { $num ->
              [one] Hello!
             *[two] World!
          }
      `;
    const entry = parseEntry(input);
    expect(findPluralSelectors(entry.value)).toMatchObject([0]);
  });

  it('returns [0] if all variant keys are numbers', () => {
    const input = ftl`
      my-entry =
          { $num ->
              [1] Hello!
             *[2] World!
          }
      `;
    const entry = parseEntry(input);
    expect(findPluralSelectors(entry.value)).toMatchObject([0]);
  });

  it('returns [0] if one variant key is a CLDR plural and the other is a number', () => {
    const input = ftl`
      my-entry =
          { $num ->
              [0] Zero!
              [one] Hello!
             *[1] World!
          }
      `;
    const entry = parseEntry(input);
    expect(findPluralSelectors(entry.value)).toMatchObject([0]);
  });

  it('returns [] if one variant key is a CLDR plural and the other is neither a CLDR plural nor a number', () => {
    const input = ftl`
      my-entry =
          { $num ->
              [some] Hello!
             *[other] World!
          }
      `;
    const entry = parseEntry(input);
    expect(findPluralSelectors(entry.value)).toMatchObject([]);
  });
});
