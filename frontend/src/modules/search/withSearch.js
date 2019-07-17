/* @flow */

import * as React from 'react';
import createMarker from 'react-content-marker';


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
        
        const rules = searchWords.map(function(searchWord) {
            return {
                rule: new RegExp(searchWord, 'i'),
                tag: searchWord => <mark className='search'>{ searchWord }</mark>,
            };
        });

        const WithSearch = createMarker(rules);

        return <WithSearch>{ base }</WithSearch>;
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
