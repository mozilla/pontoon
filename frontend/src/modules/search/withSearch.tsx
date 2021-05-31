import * as React from 'react';
import shortid from 'shortid';
import escapeRegExp from 'lodash.escaperegexp';
import { mark } from 'react-content-marker';

export function markSearchTerms(
    base: Array<React.ReactNode> | string,
    search: string,
): Array<React.ReactNode> | string {
    // Split search string on spaces except if between non-escaped quotes.
    const unusable = '☠';
    const searchTerms = search
        .replace(/\\"/g, unusable)
        .match(/[^\s"]+|"[^"]+"/g);

    if (searchTerms) {
        const reg = new RegExp(unusable, 'g');
        var i = searchTerms.length;

        while (i--) {
            searchTerms[i] = searchTerms[i].replace(/^["]|["]$/g, '');
            searchTerms[i] = searchTerms[i].replace(reg, '"');
        }

        // Sort array in decreasing order of string length
        searchTerms.sort(function (a, b) {
            return b.length - a.length;
        });

        for (let searchTerm of searchTerms) {
            const rule = new RegExp(escapeRegExp(searchTerm), 'i');
            const tag = (x: string) => (
                <mark className='search' key={shortid.generate()}>
                    {x}
                </mark>
            );

            base = mark(base, rule, tag);
        }
    }

    return base;
}

type Props = {
    search: string;
};

export default function withSearch<Config extends Record<string, any>>(
    WrappedComponent: React.ComponentType<Config>,
): React.ComponentType<Config> {
    return function WithSearch(props: Config & Props) {
        return (
            <WrappedComponent {...props}>
                {markSearchTerms(props.children, props.search)}
            </WrappedComponent>
        );
    };
}
