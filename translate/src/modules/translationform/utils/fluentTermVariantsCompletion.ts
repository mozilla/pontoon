import type {
  CompletionContext,
  CompletionSource,
} from '@codemirror/autocomplete';

import type { FluentTerms, FluentTermType } from '~/api/fluentTerms';

const MATCH_TERM_RE = /\{[ \t\n]*-([A-Za-z][\w-]*)\(([A-Za-z][\w-]*)?$/;

type VariantOptions = Array<{ selector: string; key: string }>;

function getTermVariants(value: FluentTermType['value']): VariantOptions {
  if (typeof value === 'string' || Array.isArray(value) || !('sel' in value)) {
    return [];
  }
  return value.alt.flatMap((alt) =>
    alt.keys.flatMap((key, i) =>
      typeof key === 'string' ? [{ selector: value.sel[i], key }] : [],
    ),
  );
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
      options: variants.map(({ selector, key }) => ({
        label: key,
        apply: `${selector}: "${key}"`,
        type: 'keyword',
      })),
    };
  };
}
