/* @flow */

import * as React from 'react';

import { withDiff } from 'core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from 'core/placeable';
import { withSearch } from 'modules/search';

// $FlowIgnore: I just can't get HOC working with Flow.
const TranslationPlaceablesDiff = withDiff(WithPlaceablesNoLeadingSpace);

// $FlowIgnore: I just can't get HOC working with Flow.
const TranslationPlaceablesSearch = withSearch(WithPlaceablesNoLeadingSpace);

export type TranslationProps = {|
    content: string,
    diffTarget?: ?string,
    search?: ?string,
|};

export default class GenericTranslation extends React.Component<TranslationProps> {
    render(): React.Element<React.ElementType> {
        const { content, diffTarget, search } = this.props;

        if (diffTarget) {
            return (
                <TranslationPlaceablesDiff diffTarget={diffTarget}>
                    {content}
                </TranslationPlaceablesDiff>
            );
        }

        if (search) {
            return (
                <TranslationPlaceablesSearch search={search}>
                    {content}
                </TranslationPlaceablesSearch>
            );
        }

        return <WithPlaceables>{content}</WithPlaceables>;
    }
}
