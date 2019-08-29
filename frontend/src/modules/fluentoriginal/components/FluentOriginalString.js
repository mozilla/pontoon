/* @flow */

import * as React from 'react';

import { WithPlaceables } from 'core/placeable';
import { fluent } from 'core/utils';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locales';


type Props = {|
    +entity: Entity,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


export default function FluentOriginalString(props: Props) {
    const message = fluent.parser.parseEntry(props.entity.original);
    const syntax = fluent.getSyntaxType(message);

    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceables>
            { props.entity.original }
        </WithPlaceables>
    </p>;
}
