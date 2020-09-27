/* @flow */

import * as React from 'react';
import escapeRegExp from 'lodash.escaperegexp';
import createMarker from 'react-content-marker';
import shortid from 'shortid';

import {
    getRulesWithFluent,
    getRulesWithoutLeadingSpace,
    rules,
} from 'core/placeable';

import type { TermState } from 'core/term';

export default function getMarker(terms: TermState, forFluent: ?boolean) {
    let placeableRules = getRulesWithoutLeadingSpace(rules);

    if (forFluent) {
        placeableRules = getRulesWithFluent(placeableRules);
    }

    if (terms.fetching || !terms.terms) {
        return createMarker(placeableRules);
    }

    const newRules = [...placeableRules];

    // Sort terms by length descendingly. That allows us to mark multi-word terms
    // when they consist of words that are terms as well. See test case for the example.
    const sortedTerms = terms.terms.sort((a, b) =>
        a.text.length < b.text.length ? 1 : -1,
    );

    for (let term of sortedTerms) {
        const text = escapeRegExp(term.text);

        const termParser = {
            rule: new RegExp(`\\b${text}[a-zA-z]*\\b`, 'gi'),
            tag: (x: string) => {
                return (
                    <mark
                        className='term'
                        data-term={term.text}
                        key={shortid.generate()}
                    >
                        {x}
                    </mark>
                );
            },
        };

        newRules.push(termParser);
    }

    return createMarker(newRules);
}
