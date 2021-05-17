import * as React from 'react';

import { withDiff } from 'core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from 'core/placeable';
import { withSearch } from 'modules/search';

// @ts-ignore: I just can't get HOC working with Flow.
const TranslationPlaceablesDiff = withDiff(WithPlaceablesNoLeadingSpace);

// @ts-ignore: I just can't get HOC working with Flow.
const TranslationPlaceablesSearch = withSearch(WithPlaceablesNoLeadingSpace);

export type TranslationProps = {
    content: string;
    diffTarget?: string | null | undefined;
    search?: string | null | undefined;
};

export default class GenericTranslation extends React.Component<TranslationProps> {
    render(): React.ReactElement<React.ElementType> {
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
