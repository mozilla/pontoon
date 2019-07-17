/* @flow */

import * as React from 'react';
import shortid from 'shortid';
import { mark } from 'react-content-marker';


export function highlightSearch(base: string, search: string){
    // Split search string on spaces except if between non-escaped quotes.
    const unusable = '☠';
    const searchWords = search.replace(/\\"/g, unusable).match(/[^\s"]+|"[^"]+"/g);

    if (searchWords) {
        const reg = new RegExp(unusable, 'g');
        var i = searchWords.length;

        while(i--) {
            searchWords[i] = searchWords[i].replace(/^["]|["]$/g, '');
            searchWords[i] = searchWords[i].replace(reg, '"');
        }

        // Sort array in decreasing order of string length
        searchWords.sort(function(a, b) {
            return b.length - a.length;
        });

        for (let searchWord of searchWords) {
            const rule = new RegExp(searchWord, 'i');

            const key = shortid.generate();
            const markup = <mark className='search' key={ key }>{ searchWord }</mark>;
            const tag = searchWord => markup;

            base = mark(base, rule, tag);
        }
    }

    return base;
}


type Props = {
    search: string,
};


export default function withSearch<Config: Object>(
    WrappedComponent: React.AbstractComponent<Config>
): React.AbstractComponent<Config> {
    return function WithSearch(props: { ...Config, ...Props }) {
        return <WrappedComponent { ...props }>
            { highlightSearch(props.children, props.search) }
        </WrappedComponent>;
    };
}
