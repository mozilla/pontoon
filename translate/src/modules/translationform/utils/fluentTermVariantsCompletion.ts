import type {
  CompletionContext,
  CompletionSource,
} from '@codemirror/autocomplete';

import type { FluentTermType, GetFluentTerms } from '~/api/fluentTerms';

const MAX_LOOKBEHIND = 500;

const MATCH_TERM_RE =
  /\{[ \t\n]*-([A-Za-z][\w-]*)\((?:[^),]*,)*[ \t\n]*([A-Za-z][\w-]*)?$/;

const NUMBER_LITERAL_RE = /^-?[0-9]+(?:\.[0-9]+)?$/;

export function formatArgumentValue(key: string): string {
  return NUMBER_LITERAL_RE.test(key) ? key : `"${key}"`;
}

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
  getTerms: GetFluentTerms,
): CompletionSource {
  return async (context: CompletionContext) => {
    const textBefore = context.state.doc.sliceString(
      Math.max(0, context.pos - MAX_LOOKBEHIND),
      context.pos,
    );
    const match = MATCH_TERM_RE.exec(textBefore);
    if (!match) {
      return null;
    }

    let terms: Awaited<ReturnType<GetFluentTerms>>;
    try {
      terms = await getTerms();
    } catch (err) {
      console.warn(`Cannot retrieve terms: ${err}`);
      return null;
    }

    const requestedTerm = `-${match[1]}`;
    const term = terms[requestedTerm];

    if (!term) {
      return null;
    }

    const partial = match[2] ?? '';
    const from = context.pos - partial.length;
    const args = match[0].slice(
      match[0].indexOf('(') + 1,
      match[0].length - partial.length,
    );
    const usedSelectors = new Set(
      [...args.matchAll(/(?:^|,)\s*([A-Za-z][\w-]*)\s*:/g)].map(
        ([, selector]) => selector,
      ),
    );

    const variants = getTermVariants(
      term.translation_value ?? term.value,
    ).filter(({ selector }) => !usedSelectors.has(selector));
    if (!variants.length) {
      return null;
    }

    return {
      from,
      to: context.pos,
      validFor: /^[A-Za-z][\w-]*$/,
      options: variants.flatMap(({ selector, keys }, groupIndex) =>
        keys.map(({ key, isDefault }, keyIndex) => ({
          label: `${selector}: ${formatArgumentValue(key)}`,
          detail: isDefault ? 'default' : undefined,
          type: 'keyword',
          // Keep each group sorted the same way they are defined.
          // Note the default comes last as per `getTermVariants()` sorting.
          boost: -groupIndex * 100 - keyIndex,
        })),
      ),
    };
  };
}
