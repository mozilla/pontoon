/* @flow */

import * as React from 'react';

import { withDiff } from 'core/diff';
import { WithPlaceablesForFluent, WithPlaceablesForFluentNoLeadingSpace } from 'core/placeable';
import { fluent } from 'core/utils';

import type { TranslationProps } from './GenericTranslation';


// $FLOW_IGNORE: I just can't get HOC working with Flow.
const TranslationPlaceablesDiff = withDiff(WithPlaceablesForFluentNoLeadingSpace);


export default class FluentTranslation extends React.Component<TranslationProps> {
    render() {
        const { content, diffTarget } = this.props;

        if (diffTarget) {
            const fluentTarget = fluent.getSimplePreview(diffTarget);
            return <TranslationPlaceablesDiff diffTarget={ fluentTarget }>
                { fluent.getSimplePreview(content) }
            </TranslationPlaceablesDiff>;
        }

        return <WithPlaceablesForFluent>
            { fluent.getSimplePreview(content) }
        </WithPlaceablesForFluent>;
    }
}
