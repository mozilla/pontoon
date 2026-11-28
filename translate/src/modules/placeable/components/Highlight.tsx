import { Localized } from '@fluent/react';
import escapeRegExp from 'lodash.escaperegexp';
import React, { useContext, type ReactElement } from 'react';
import { TermState } from '~/modules/terms';
import { Location } from '~/context/Location';

import './Highlight.css';
import { placeholder } from '../placeholder';

let keyCounter = 0;

/**
 * Component that marks placeables and terms in a string.
 */
export function Highlight({
  children,
  search,
  terms,
}: {
  children: string;
  search?: string | null;
  terms?: TermState;
}) {
  const source = String(children);
  const marks: Array<{
    index: number;
    length: number;
    mark: ReactElement;
  }> = [];
  const location = useContext(Location);

  for (const match of source.matchAll(placeholder)) {
    let l10nId: string;
    let hidden = '';
    // Code-like placeables are isolated as LTR, so that their
    // neutral characters (e.g. `<`, `/`, `>`) are not reordered in RTL text.
    let ltr = true;
    const text = match[0];
    switch (text[0]) {
      case '<':
        l10nId = 'highlight-placeholder-html';
        break;
      case '{':
      case '$':
        l10nId = 'highlight-placeholder';
        break;
      case '%':
        l10nId = 'highlight-placeholder-printf';
        break;
      case '&':
        l10nId = 'highlight-placeholder-entity';
        break;
      case '\\':
        l10nId = 'highlight-escape';
        break;
      case '-':
        // `-1` also looks like a CLI option, but is a negative number
        l10nId = /^-\d$/.test(text)
          ? 'highlight-number'
          : 'highlight-cli-option';
        break;
      case 'f':
      case 'h':
        l10nId = 'highlight-url';
        break;
      case '\n':
        l10nId = 'highlight-newline';
        hidden = '¶';
        ltr = false;
        break;
      case '\t':
        l10nId = 'highlight-tab';
        hidden = ' →';
        ltr = false;
        break;
      default:
        l10nId = /^\s/.test(text)
          ? 'highlight-spaces'
          : 'highlight-punctuation';
        ltr = false;
    }
    marks.push({
      index: match.index ?? -1,
      length: text.length,
      mark: (
        <Localized id={l10nId} attrs={{ title: true }} key={++keyCounter}>
          <mark
            className='placeable'
            data-match={text}
            dir={ltr ? 'ltr' : undefined}
          >
            {hidden ? <span aria-hidden>{hidden}</span> : null}
            {text}
          </mark>
        </Localized>
      ),
    });
  }

  for (const { l10nId, re } of [
    { l10nId: 'highlight-email', re: /(?:mailto:)?\w[\w.-]*@\w[\w.]*\w/g },
    {
      l10nId: 'highlight-number',
      // Latin and Persian digits, with Persian decimal and thousands separators
      re: /[-+\u2212]?[0-9\u06F0-\u06F9]+(?:[\u00A0.,\u066B\u066C][0-9\u06F0-\u06F9]+)*(?![\w\u06F0-\u06F9])/gu,
    },
  ]) {
    for (const match of source.matchAll(re)) {
      const text = match[0];
      const index = match.index ?? -1;
      // Signed numbers are isolated as LTR to keep the sign on the left of
      // the digits in RTL text, as in CLDR (e.g. U+200E U+2212 for Persian).
      // In ranges like `1-2` the dash is not a sign.
      const signed =
        /^[-+\u2212]/.test(text) &&
        !/[\w\u06f0-\u06f9]/.test(source[index - 1] ?? '');
      marks.push({
        index,
        length: text.length,
        mark: (
          <Localized id={l10nId} attrs={{ title: true }} key={++keyCounter}>
            <mark
              className='placeable'
              data-match={text}
              dir={signed ? 'ltr' : undefined}
            >
              {text}
            </mark>
          </Localized>
        ),
      });
    }
  }

  const lcSource = source.toLowerCase();

  if (terms?.terms && !terms.fetching) {
    const sourceTerms = terms.terms
      .filter((t) => lcSource.includes(t.text.toLowerCase()))
      .map((t) => t.text)
      .sort((a, b) => (a.length < b.length ? 1 : -1));
    for (const term of sourceTerms) {
      const re = new RegExp(`\\b${escapeRegExp(term)}[a-zA-Z]*\\b`, 'gi');
      for (const match of source.matchAll(re)) {
        marks.push({
          index: match.index ?? -1,
          length: match[0].length,
          mark: (
            <mark className='term' data-match={term} key={++keyCounter}>
              {match[0]}
            </mark>
          ),
        });
      }
    }
  }

  // Sort by position, prefer longer marks
  marks.sort((a, b) => a.index - b.index || b.length - a.length);

  if (search) {
    let regexp: RegExp;
    try {
      regexp = new RegExp(String.raw`(?<!\\)"(?:\\"|[^"])+(?<!\\)"|\S+`, 'g');
    } catch {
      // Fallback for older browsers (e.g. iOS 15) not supporting lookbehind.
      regexp = /"(?:\\"|[^"])+"|\S+/g;
    }
    const searchTerms = search.match(regexp);

    for (let term of searchTerms ?? []) {
      if (term.startsWith('"') && term.length >= 3 && term.endsWith('"')) {
        term = term.slice(1, -1);
      }
      let next: number;
      const regexFlags = location.search_match_case ? 'g' : 'gi';
      const re = location.search_match_whole_word
        ? new RegExp(`\\b${escapeRegExp(term)}\\b`, regexFlags)
        : new RegExp(`${escapeRegExp(term)}`, regexFlags);
      let match;

      while ((match = re.exec(source)) !== null) {
        next = match.index;
        let i = marks.findIndex((m) => m.index + m.length > next);
        if (i === -1) {
          i = marks.length;
        }
        marks.splice(i, 0, {
          index: next,
          length: term.length,
          mark: (
            <mark className='search' key={++keyCounter}>
              {source.substring(next, next + term.length)}
            </mark>
          ),
        });
      }
    }
  }

  const res: Array<string | ReactElement> = [];
  let pos = 0;
  for (const { index, length, mark } of marks) {
    if (index > pos) {
      res.push(source.slice(pos, index));
    }
    if (index >= pos) {
      res.push(mark);
      pos = index + length;
    }
  }
  if (pos < source.length) {
    res.push(source.slice(pos));
  }
  return <>{res}</>;
}
