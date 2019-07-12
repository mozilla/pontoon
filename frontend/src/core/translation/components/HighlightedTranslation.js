/* @flow */

import * as React from 'react';
import Highlighter from 'react-highlight-words';


type Props = {|
    searchWords: Array<string>,
    textToHighlight: string,
|};


export default class HighlightedTranslation extends React.Component<Props> {
    render() {
        const { searchWords, textToHighlight } = this.props;

        const unusable = '☠';
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

        return <Highlighter
            highlightClassName='search'
            searchWords={ searchWords }
            autoEscape={ true }
            textToHighlight={ textToHighlight }
        />
    }
}
