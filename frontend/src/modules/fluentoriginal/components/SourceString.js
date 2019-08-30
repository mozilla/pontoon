/* @flow */

import * as React from 'react';

import { WithPlaceablesForFluent } from 'core/placeable';

import type { Entity } from 'core/api';


type Props = {|
    +entity: Entity,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


/**
 * Show the source string of a Fluent entity.
 */
export default function SourceString(props: Props) {
    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceablesForFluent>
            { props.entity.original }
        </WithPlaceablesForFluent>
    </p>;
}
