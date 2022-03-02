import * as React from 'react';

import { withDiff } from '~/core/diff';
import {
    WithPlaceablesForFluent,
    WithPlaceablesForFluentNoLeadingSpace,
} from '~/core/placeable';
import { fluent } from '~/core/utils';
import { withSearch } from '~/modules/search';

import type { TranslationProps } from './GenericTranslation';

// @ts-ignore: https://github.com/mozilla/pontoon/issues/2294.
const TranslationPlaceablesDiff = withDiff(
    WithPlaceablesForFluentNoLeadingSpace,
);

// @ts-ignore: https://github.com/mozilla/pontoon/issues/2294.
const TranslationPlaceablesSearch = withSearch(
    WithPlaceablesForFluentNoLeadingSpace,
);

export default function FluentTranslation({
    content,
    diffTarget,
    search,
}: TranslationProps): React.ReactElement<React.ElementType> {
    const preview = fluent.getSimplePreview(content);

    if (diffTarget) {
        const fluentTarget = fluent.getSimplePreview(diffTarget);
        return (
            <TranslationPlaceablesDiff diffTarget={fluentTarget}>
                {preview}
            </TranslationPlaceablesDiff>
        );
    }

    if (search) {
        return (
            <TranslationPlaceablesSearch search={search}>
                {preview}
            </TranslationPlaceablesSearch>
        );
    }

    return <WithPlaceablesForFluent>{preview}</WithPlaceablesForFluent>;
}
