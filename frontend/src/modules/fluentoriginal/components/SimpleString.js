/* @flow */

import * as React from 'react';

import { WithPlaceablesForFluent } from 'core/placeable';
import { fluent } from 'core/utils';

import type { Entity } from 'core/api';


type Props = {|
    +entity: Entity,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


/**
 * Show the original string of a Fluent entity as a simple preview.
 */
export default function SimpleString(props: Props) {
    const original = fluent.getSimplePreview(props.entity.original);

    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceablesForFluent>
            { original }
        </WithPlaceablesForFluent>
    </p>;
}
