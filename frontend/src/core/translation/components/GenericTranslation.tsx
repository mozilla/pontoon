import * as React from 'react';

import { withDiff } from 'core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from 'core/placeable';
import { withSearch } from 'modules/search';

const TranslationPlaceablesDiff = withDiff(WithPlaceablesNoLeadingSpace);

const TranslationPlaceablesSearch = withSearch(WithPlaceablesNoLeadingSpace);

export type TranslationProps = {
    content: string;
    diffTarget?: string | null | undefined;
    search?: string | null | undefined;
};

export default class GenericTranslation extends React.Component<TranslationProps> {
    render() {
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
