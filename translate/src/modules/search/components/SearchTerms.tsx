import escapeRegExp from 'lodash.escaperegexp';
import React from 'react';
import { mark } from 'react-content-marker';

let keyCounter = 0;

export function SearchTerms({
  children,
  search,
}: {
  children: string;
  search: string;
}): React.ReactElement {
  // Split search string on spaces except if between non-escaped quotes.
  const unusable = '☠';
  const searchTerms = search
    .replace(/\\"/g, unusable)
    .match(/[^\s"]+|"[^"]+"/g);

  if (!searchTerms) {
    return <>{children}</>;
  }

  const reg = new RegExp(unusable, 'g');
  for (let i = searchTerms.length - 1; i >= 0; --i) {
    searchTerms[i] = searchTerms[i].replace(/^["]|["]$/g, '').replace(reg, '"');
  }

  // Sort array in decreasing order of string length
  searchTerms.sort((a, b) => b.length - a.length);

  let res: React.ReactNode[] = [children];
  for (let searchTerm of searchTerms) {
    const rule = new RegExp(escapeRegExp(searchTerm), 'i');
    const tag = (x: string) => (
      <mark className='search' key={++keyCounter}>
        {x}
      </mark>
    );

    res = mark(res, rule, tag);
  }

  return <>{res}</>;
}
