/* @flow */

import * as React from 'react';
import shortid from 'shortid';
import escapeRegExp from 'lodash.escaperegexp';
import { mark } from 'react-content-marker';

import type { TermState } from 'core/term';


export function markTerms(base: string, terms: TermState) {
    if (terms.fetching || !terms.terms) {
        return base;
    }

    // Sort terms by length descendingly. That allows us to mark multi-word terms
    // when they consist of words that are terms as well. See test case for the example.
    const sortedTerms = terms.terms.sort((a, b) => (a.text.length < b.text.length) ? 1 : -1);

    for (let term of sortedTerms) {
        const text = escapeRegExp(term.text);
        const rule = new RegExp(`\\b${text}[a-zA-z]*\\b`, 'gi');
        const tag = (x: string) =>
            <mark
                className='term'
                data-term={ term.text }
                key={ shortid.generate() }
            >{ x }</mark>;

        base = mark(base, rule, tag);
    }

    return base;
}


type Props = {|
    terms: TermState,
|};


export default function withTerms<Config: Object>(
    WrappedComponent: React.AbstractComponent<Config>
): React.AbstractComponent<Config> {
    return function WithTerms(props: { ...Config, ...Props }) {
        return <WrappedComponent { ...props }>
            { markTerms(props.children, props.terms) }
        </WrappedComponent>;
    };
}
