import { CompletionContext } from '@codemirror/autocomplete';
import { EditorState } from '@codemirror/state';

import {
  fluentTermVariantsCompletion,
  getTermVariants,
} from './fluentTermVariantsCompletion';

import type { SelectMessage } from '@mozilla/l10n';
import type { FluentTermType, FluentTerms } from '~/api/fluentTerms';
import type { VariantOptions } from './fluentTermVariantsCompletion';

const terms: FluentTerms = {
  '-brand-name': {
    value: {
      decl: {},
      sel: ['case'],
      alt: [
        { keys: ['nominative'], pat: ['Brand'] },
        { keys: ['accusative'], pat: ['the Brand'] },
        { keys: [{ '*': '' }], pat: ['Brand'] },
      ],
    },
    properties: null,
    translation_value: {
      decl: {},
      sel: ['case'],
      alt: [
        { keys: ['nor'], pat: ['marka'] },
        { keys: ['nork'], pat: ['markak'] },
        { keys: [{ '*': '' }], pat: ['marka'] },
      ],
    },
    translation_properties: null,
  },
  '-plain-term': {
    value: ['Just a pattern'],
    properties: null,
    translation_value: null,
    translation_properties: null,
  },
};

describe('getTermVariants', () => {
  const select = (
    sel: string | SelectMessage['sel'],
    alt: SelectMessage['alt'],
  ): FluentTermType['value'] => ({
    decl: {},
    sel: [sel].flat(),
    alt,
  });

  const variantKeys = (variants: VariantOptions) =>
    variants.map(({ selector, keys }) => ({
      selector,
      keys: keys.map(({ key }) => key),
    }));

  it('returns no variants for plain pattern terms', () => {
    expect(getTermVariants(['Just a pattern'])).toEqual([]);
  });

  it('groups keys by selector and dedupes them', () => {
    const value = select('case', [
      { keys: ['nor'], pat: ['marka'] },
      { keys: ['nork'], pat: ['markak'] },
      { keys: [{ '*': '' }], pat: ['marka'] },
    ]);

    const variants = getTermVariants(value);

    expect(variantKeys(variants)).toEqual([
      { selector: 'case', keys: ['nor', 'nork'] },
    ]);
  });

  it('zips keys with selectors within each variant', () => {
    const value = select(
      ['case', 'count'],
      [
        { keys: ['nom', 'one'], pat: ['CD'] },
        { keys: ['nom', 'two'], pat: ['CDs'] },
        { keys: ['acc', 'one'], pat: ['the CD'] },
      ],
    );

    const variants = getTermVariants(value);

    expect(variantKeys(variants)).toEqual([
      { selector: 'case', keys: ['nom', 'acc'] },
      { selector: 'count', keys: ['one', 'two'] },
    ]);
  });

  it('uses the catchall key name when present', () => {
    const value = select(
      ['capitalize', 'case', 'number'],
      [
        { keys: ['yes', 'nork', 'sing'], pat: ['Leiho adimendunak'] },
        { keys: ['yes', 'nork', 'pl'], pat: ['Leiho adimendunek'] },
        { keys: ['yes', 'nork', { '*': 'mugg' }], pat: ['Leiho adimendunek'] },
        { keys: ['yes', { '*': 'nor' }, 'sing'], pat: ['Leiho adimenduna'] },
        { keys: ['yes', { '*': 'nor' }, 'pl'], pat: ['Leiho adimendunak'] },
        { keys: [{ '*': 'no' }, 'nork', 'sing'], pat: ['leiho adimendunak'] },
        {
          keys: [{ '*': 'no' }, { '*': 'nor' }, { '*': 'mugg' }],
          pat: ['leiho adimendun'],
        },
      ],
    );

    const variants = getTermVariants(value);

    expect(variantKeys(variants)).toEqual([
      { selector: 'capitalize', keys: ['yes', 'no'] },
      { selector: 'case', keys: ['nork', 'nor'] },
      { selector: 'number', keys: ['sing', 'pl', 'mugg'] },
    ]);
    expect(
      variants.map(({ keys }) => keys.findLast(({ isDefault }) => isDefault)),
    ).toEqual([
      { key: 'no', isDefault: true },
      { key: 'nor', isDefault: true },
      { key: 'mugg', isDefault: true },
    ]);
  });
});

describe('fluentTermVariantsCompletion', () => {
  const getTerms = vi.fn(async () => terms);
  const source = fluentTermVariantsCompletion(getTerms, 'acme', 'ab');

  function complete(doc: string, pos: number = doc.length) {
    const state = EditorState.create({ doc });
    const context = new CompletionContext(state, pos, false);
    return source(context);
  }

  beforeEach(() => {
    getTerms.mockClear();
  });

  it('completes term variants after the trigger', async () => {
    const doc = '{ -brand-name(';
    const result = await complete(doc);

    expect(result).not.toBeNull();
    expect(result!.from).toBe(doc.length);
    expect(result!.options.map((option) => option.label)).toEqual([
      'case: "nor"',
      'case: "nork"',
    ]);
  });

  it('completes in the middle of the text', async () => {
    const doc = '{ -brand-name( }';
    // Position at parenthesis
    const pos = doc.slice(0, -2).length;
    const result = await complete(doc, pos);

    expect(result).not.toBeNull();
    expect(result!.from).toBe(pos);
    expect(result!.options.map((option) => option.label)).toEqual([
      'case: "nor"',
      'case: "nork"',
    ]);
  });

  it('allows whitespace between the brace and the term', async () => {
    const doc = '{  -brand-name(';
    const result = await complete(doc);

    expect(result).not.toBeNull();
    expect(result!.options.map((option) => option.label)).toEqual([
      'case: "nor"',
      'case: "nork"',
    ]);
  });

  it('returns all variants for the term', async () => {
    const doc = '{ -brand-name(asdf';
    const result = await complete(doc);

    expect(result).not.toBeNull();
    expect(result!.from).toBe('{ -brand-name('.length);
    expect(result!.options.map((option) => option.label)).toEqual([
      'case: "nor"',
      'case: "nork"',
    ]);
  });

  it('falls back to source variants', async () => {
    getTerms.mockResolvedValueOnce({
      ...terms,
      '-brand-name': { ...terms['-brand-name'], translation_value: null },
    });

    const doc = '{ -brand-name(';
    const result = await complete(doc);

    expect(result).not.toBeNull();
    expect(result!.from).toBe(doc.length);
    expect(result!.options.map((option) => option.label)).toEqual([
      'case: "nominative"',
      'case: "accusative"',
    ]);
  });

  it('ignores unknown terms', async () => {
    const result = await complete('{ -unknown-term(');

    expect(result).toBeNull();
  });

  it('ignores terms without variants', async () => {
    const result = await complete('{ -plain-term(');

    expect(result).toBeNull();
  });

  it('ignores terms missing the opening parenthesis', async () => {
    expect(await complete('{ -brand-name')).toBeNull();
    expect(await complete('{ -brand-name }')).toBeNull();
  });

  it('ignores non-term placeables', async () => {
    expect(await complete('{ $variable(')).toBeNull();
    expect(await complete('{ other-message(')).toBeNull();
    expect(await complete('{ -brand-name.attr(')).toBeNull();
  });

  it('handles concurrent trigger requests', async () => {
    const [a, b] = await Promise.all([
      complete('{ -brand-name('),
      complete('{ -brand-name('),
    ]);

    expect(a).not.toBeNull();
    expect(b).not.toBeNull();
    expect(a!.options).toEqual(b!.options);
  });
});
