/* @flow */

import * as React from 'react';

import { withDiff } from 'core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from 'core/placeable';


// $FLOW_IGNORE: I just can't get HOC working with Flow.
const TranslationPlaceablesDiff = withDiff(WithPlaceablesNoLeadingSpace);


export type TranslationProps = {|
    content: string,
    diffTarget: ?string,
|};


export default class GenericTranslation extends React.Component<TranslationProps> {
    render() {
        const { content, diffTarget } = this.props;

        if (diffTarget) {
            return <TranslationPlaceablesDiff diffTarget={ diffTarget }>
                { content }
            </TranslationPlaceablesDiff>;
        }

        return <WithPlaceables>{ content }</WithPlaceables>;
    }
}
