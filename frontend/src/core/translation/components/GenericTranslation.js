/* @flow */

import * as React from 'react';

import HighlightedTranslation from './HighlightedTranslation';
import { withDiff } from 'core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from 'core/placeable';


// $FLOW_IGNORE: I just can't get HOC working with Flow.
const TranslationPlaceablesDiff = withDiff(WithPlaceablesNoLeadingSpace);


export type TranslationProps = {|
    content: string,
    diffTarget: ?string,
    search: ?string,
|};


export default class GenericTranslation extends React.Component<TranslationProps> {
    render() {
        const { content, diffTarget, search } = this.props;

        if (diffTarget) {
            return <TranslationPlaceablesDiff diffTarget={ diffTarget }>
                { content }
            </TranslationPlaceablesDiff>;
        }

        if (search) {
            // Split search string on spaces except if between non-escaped quotes.
            const searchWords = search.replace(/\\"/g, '☠').match(/[^\s"]+|"[^"]+"/g);

            if (searchWords) {
                return <HighlightedTranslation
                    searchWords={ searchWords }
                    textToHighlight={ content }
                />;
            }
        }

        return <WithPlaceables>{ content }</WithPlaceables>;
    }
}
