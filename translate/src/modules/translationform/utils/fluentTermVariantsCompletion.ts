import type {
  CompletionContext,
  CompletionSource,
} from '@codemirror/autocomplete';

import type { FluentTerms, FluentTermType } from '~/api/fluentTerms';

const MATCH_TERM_RE = /\{[ \t\n]*-([A-Za-z][\w-]*)\(([A-Za-z][\w-]*)?$/;

export type VariantOptions = Array<{
  selector: string;
  keys: Array<{ key: string; isDefault: boolean }>;
}>;

export function getTermVariants(
  value: FluentTermType['value'],
): VariantOptions {
  if (Array.isArray(value) || !('sel' in value)) {
    return [];
  }

  const keysBySelector = new Map<
    string,
    { keys: Set<string>; defaultKeys: Set<string> }
  >();
  for (const alt of value.alt) {
    for (const [i, selector] of value.sel.entries()) {
      const rawKey = alt.keys[i];
      let key: string;
      const isDefault = typeof rawKey !== 'string';
      if (isDefault) {
        if (!rawKey['*']) {
          continue;
        }
        key = rawKey['*'];
      } else {
        key = rawKey;
      }
      let group = keysBySelector.get(selector);
      if (!group) {
        group = { keys: new Set(), defaultKeys: new Set() };
        keysBySelector.set(selector, group);
      }
      group.keys.add(key);
      if (isDefault) {
        group.defaultKeys.add(key);
      }
    }
  }

  return keysBySelector
    .entries()
    .map(([selector, { keys, defaultKeys }]) => ({
      selector,
      keys: [...keys]
        .map((key) => ({ key, isDefault: defaultKeys.has(key) }))
        .sort((a, b) => Number(a.isDefault) - Number(b.isDefault)),
    }))
    .toArray();
}

export function fluentTermVariantsCompletion(
  getTerms: (project: string, locale: string) => Promise<FluentTerms>,
  project: string,
  locale: string,
): CompletionSource {
  return async (context: CompletionContext) => {
    const textBefore = context.state.doc.sliceString(0, context.pos);
    const match = MATCH_TERM_RE.exec(textBefore);
    if (!match) {
      return null;
    }

    let terms: FluentTerms;
    try {
      terms = await getTerms(project, locale);
    } catch (err) {
      console.warn(`Cannot retrieve terms for ${project}/${locale}: ${err}`);
      return null;
    }

    const parenIdx = match.index + match[0].indexOf('(');
    const requestedTerm = `-${match[1]}`;
    const term = terms[requestedTerm];

    if (!term) {
      return null;
    }

    const variants = getTermVariants(term.translation_value ?? term.value);
    if (!variants.length) {
      return null;
    }

    return {
      from: parenIdx + 1,
      to: context.pos,
      validFor: /^[A-Za-z][\w-]*$/,
      options: variants.flatMap(({ selector, keys }, groupIndex) =>
        keys.map(({ key }, keyIndex) => ({
          label: `${selector}: "${key}"`,
          type: 'keyword',
          // Keep each group sorted the same way they are defined.
          // Note the default comes last as per `getTermVariants()` sorting.
          boost: -groupIndex * 100 - keyIndex,
        })),
      ),
    };
  };
}
