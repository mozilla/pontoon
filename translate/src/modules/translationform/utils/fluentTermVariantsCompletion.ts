import type {
  CompletionContext,
  CompletionSource,
} from '@codemirror/autocomplete';

import type { FluentTerms, FluentTermType } from '~/api/fluentTerms';

const MATCH_TERM_RE = /\{[ \t\n]*-([A-Za-z][\w-]*)\(([A-Za-z][\w-]*)?$/;

type VariantOptions = Array<{ selector: string; keys: Array<string> }>;

export function getTermVariants(
  value: FluentTermType['value'],
): VariantOptions {
  if (Array.isArray(value) || !('sel' in value)) {
    return [];
  }

  const keysBySelector = new Map<string, Set<string>>();
  for (const alt of value.alt) {
    for (const [i, selector] of value.sel.entries()) {
      let key = alt.keys[i];
      if (typeof key !== 'string') {
        if (!key['*']) {
          continue;
        }
        key = key['*'];
      }
      let keys = keysBySelector.get(selector);
      if (!keys) {
        keys = new Set();
        keysBySelector.set(selector, keys);
      }
      keys.add(key);
    }
  }

  return [...keysBySelector].map(([selector, keys]) => ({
    selector,
    keys: [...keys],
  }));
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
      options: variants.flatMap(({ selector, keys }) =>
        keys.map((key) => ({
          label: `${selector}: "${key}"`,
          type: 'keyword',
        })),
      ),
    };
  };
}
