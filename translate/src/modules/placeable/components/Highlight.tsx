import { Localized } from '@fluent/react';
import escapeRegExp from 'lodash.escaperegexp';
import { cloneElement, ReactNode } from 'react';
import createMarker, { getRules, Parser } from 'react-content-marker';
import { TermState } from '~/modules/terms';

import './Highlight.css';

let keyCounter = 0;
const MarkerCache = new Map<string, ReturnType<typeof createMarker>>();

/**
 * Component that marks placeables and terms in a string.
 */
export function Highlight({
  children,
  fluent = false,
  leadingSpaces = false,
  terms,
}: {
  children: ReactNode | ReactNode[];
  fluent?: boolean;
  leadingSpaces?: boolean;
  terms?: TermState;
}) {
  let textTerms: string[] = [];
  if (terms && !terms.fetching && terms.terms) {
    textTerms = terms.terms
      .map((t) => t.text)
      .sort((a, b) => (a.length < b.length ? 1 : -1));
  }
  const mk = [fluent, leadingSpaces].join() + '|' + textTerms.join();
  let Marker = MarkerCache.get(mk);
  if (!Marker) {
    const rules = getRules({ fluent, leadingSpaces });

    // Sort terms by length descendingly. That allows us to mark multi-word terms
    // when they consist of words that are terms as well. See test case for the example.
    for (let term of textTerms) {
      const text = escapeRegExp(term);
      const termParser = {
        rule: new RegExp(`\\b${text}[a-zA-z]*\\b`, 'gi'),
        tag: (x: string) => (
          <mark className='term' data-match={term}>
            {x}
          </mark>
        ),
      };
      rules.push(termParser);
    }

    const wrapTag = (tag: Parser['tag']) => (x: string) => {
      const el = tag(x);
      const mId = el.props['data-mark'];
      return mId ? (
        <Localized
          id={`placeable-parser-${mId}`}
          attrs={{ title: true }}
          key={++keyCounter}
        >
          {cloneElement(el, { className: 'placeable' })}
        </Localized>
      ) : (
        cloneElement(el, { key: ++keyCounter })
      );
    };
    Marker = createMarker(rules, wrapTag);
    MarkerCache.set(mk, Marker);
  }
  return <Marker>{children}</Marker>;
}
