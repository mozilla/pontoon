/* @flow */

import * as React from 'react';

import { WithPlaceables } from 'core/placeable';
import { fluent } from 'core/utils';

import type { Entity } from 'core/api';


type Props = {|
    +entity: Entity,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


export default function SimpleString(props: Props) {
    const original = fluent.getSimplePreview(props.entity.original);

    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceables>
            { original }
        </WithPlaceables>
    </p>;
}
