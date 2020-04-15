/* @flow */

import * as React from 'react';

import { WithPlaceablesForFluentNoLeadingSpace } from 'core/placeable';
import { withTerms } from 'core/term';
import { fluent } from 'core/utils';

import type { Entity } from 'core/api';
import type { TermState } from 'core/term';


type Props = {|
    +entity: Entity,
    +terms: TermState,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


const WithPlaceablesTerms = withTerms(WithPlaceablesForFluentNoLeadingSpace);


/**
 * Show the original string of a Fluent entity as a simple preview.
 */
export default function SimpleString(props: Props) {
    const original = fluent.getSimplePreview(props.entity.original);

    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceablesTerms terms={ props.terms }>
            { original }
        </WithPlaceablesTerms>
    </p>;
}
