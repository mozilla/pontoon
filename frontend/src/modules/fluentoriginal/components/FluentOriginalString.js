/* @flow */

import * as React from 'react';

import { WithPlaceablesForFluent } from 'core/placeable';
import { fluent } from 'core/utils';

import RichString from './RichString';
import SimpleString from './SimpleString';

import type { Entity } from 'core/api';


type Props = {|
    +entity: Entity,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


export default function FluentOriginalString(props: Props) {
    const message = fluent.parser.parseEntry(props.entity.original);
    const syntax = fluent.getSyntaxType(message);

    if (syntax === 'simple') {
        return <SimpleString
            entity={ props.entity }
            handleClickOnPlaceable={ props.handleClickOnPlaceable }
        />;
    }

    if (syntax === 'rich') {
        return <RichString
            entity={ props.entity }
            handleClickOnPlaceable={ props.handleClickOnPlaceable }
        />;
    }

    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceablesForFluent>
            { props.entity.original }
        </WithPlaceablesForFluent>
    </p>;
}
