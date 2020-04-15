/* @flow */

import * as React from 'react';

import { WithPlaceablesForFluentNoLeadingSpace } from 'core/placeable';
import { withTerms } from 'core/term';

import type { Entity } from 'core/api';
import type { TermState } from 'core/term';


type Props = {|
    +entity: Entity,
    +terms: TermState,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


const WithPlaceablesTerms = withTerms(WithPlaceablesForFluentNoLeadingSpace);


/**
 * Show the source string of a Fluent entity.
 */
export default function SourceString(props: Props) {
    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceablesTerms terms={ props.terms }>
            { props.entity.original }
        </WithPlaceablesTerms>
    </p>;
}
