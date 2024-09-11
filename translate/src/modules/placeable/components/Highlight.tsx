import { Localized } from '@fluent/react';
import escapeRegExp from 'lodash.escaperegexp';
import React, { useContext } from 'react';
import { TermState } from '~/modules/terms';
import { Location } from '~/context/Location';

import './Highlight.css';
import { ReactElement } from 'react';

let keyCounter = 0;

const placeholder = (() => {
  // HTML/XML <tags>
  const html = '<(?:(?:"[^"]*")|(?:\'[^\']*\')|[^>])*>';
  // Fluent & other similar {placeholders}
  const curly = '{(?:(?:"[^"]*")|[^}])*}';
  // All printf-ish formats, including Python's.
  // Excludes Python's ` ` conversion flag, due to false positives -- https://github.com/mozilla/pontoon/issues/2988
  const printf =
    "%(?:\\d\\$|\\(.*?\\))?[-+0'#I]*[\\d*]*(?:\\.[\\d*])?(?:hh?|ll?|[jLtz])?[%@AaCcdEeFfGginopSsuXx]";
  // Qt placeholders -- https://doc.qt.io/qt-5/qstring.html#arg
  const qt = '%L?\\d{1,2}';
  // HTML/XML &entities;
  const entity = '&(?:[\\w.-]+|#(?:\\d{1,5}|x[a-fA-F0-9]{1,5})+);';
  // $foo$ and $bar styles, used e.g. in webextension localization
  const dollar = '\\$\\w+\\$?';

  // all whitespace except for usual single spaces within the message
  const spaces = '[\n\t]|(?:^| )[^\\S\n\t]+|[^\\S\n\t]+$|[^\\S \n\t]+';
  // punctuation
  const punct = '[™©®℃℉°±πθ×÷−√∞∆Σ′″‘’ʼ‚‛“”„‟«»£¥€…—–]+';
  // \ escapes
  const escape = '\\\\(?:[nrt\'"\\\\]|u[0-9A-Fa-f]{4}|(?=\\n))';
  // Command-line --options and -s shorthands
  const cli = '\\B(?:-\\w|--[\\w-]+)\\b';
  // URL
  const url =
    // protocol       host         port          path & query                   end
    '(?:ftp|https?)://\\w[\\w.]*\\w(?::\\d{1,5})?(?:/[\\w$.+!*(),;:@&=?/~#%-]*)?(?=$|[\\s\\]\'"}>),.])';

  return new RegExp(
    [html, curly, printf, qt, entity, dollar, spaces, punct, escape, cli, url]
      .map((x) => `(?:${x})`)
      .join('|'),
    'g',
  );
})();

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
        l10nId = 'highlight-cli-option';
        break;
      case 'f':
      case 'h':
        l10nId = 'highlight-url';
        break;
      case '\n':
        l10nId = 'highlight-newline';
        hidden = '¶';
        break;
      case '\t':
        l10nId = 'highlight-tab';
        hidden = ' →';
        break;
      default:
        l10nId = /^\s/.test(text)
          ? 'highlight-spaces'
          : 'highlight-punctuation';
    }
    marks.push({
      index: match.index ?? -1,
      length: text.length,
      mark: (
        <Localized id={l10nId} attrs={{ title: true }} key={++keyCounter}>
          <mark className='placeable' data-match={text}>
            {hidden ? <span aria-hidden>{hidden}</span> : null}
            {text}
          </mark>
        </Localized>
      ),
    });
  }

  for (const { l10nId, re } of [
    { l10nId: 'highlight-email', re: /(?:mailto:)?\w[\w.-]*@\w[\w.]*\w/g },
    { l10nId: 'highlight-number', re: /[-+]?\d+(?:[\u00A0.,]\d+)*\b/gu },
  ]) {
    for (const match of source.matchAll(re)) {
      const text = match[0];
      marks.push({
        index: match.index ?? -1,
        length: text.length,
        mark: (
          <Localized id={l10nId} attrs={{ title: true }} key={++keyCounter}>
            <mark className='placeable' data-match={text}>
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
      const re = new RegExp(`\\b${escapeRegExp(term)}[a-zA-z]*\\b`, 'gi');
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
    const searchTerms = search.match(/(?<!\\)"(?:\\"|[^"])+(?<!\\)"|\S+/g);
    for (let term of searchTerms ?? []) {
      if (term.startsWith('"') && term.length >= 3 && term.endsWith('"')) {
        term = term.slice(1, -1);
      }
      const highlightSource = location.search_match_case ? source : lcSource;
      let next: number;
      const regexFlags = location.search_match_case ? 'g' : 'gi';
      const re = location.search_match_whole_word
        ? new RegExp(`\\b${escapeRegExp(term)}\\b`, regexFlags)
        : new RegExp(`${escapeRegExp(term)}`, regexFlags);
      let match;

      while ((match = re.exec(highlightSource)) !== null) {
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
