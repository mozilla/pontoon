/* @flow */

import * as React from 'react';

import { withTermsAndPlaceables } from 'core/term';

import type { Entity } from 'core/api';
import type { TermState } from 'core/term';


type Props = {|
    +entity: Entity,
    +terms: TermState,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


/**
 * Show the source string of a Fluent entity.
 */
export default function SourceString(props: Props) {
    const WithTermsAndPlaceables = withTermsAndPlaceables(props.terms);

    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithTermsAndPlaceables>
            { props.entity.original }
        </WithTermsAndPlaceables>
    </p>;
}
