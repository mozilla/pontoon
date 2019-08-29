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


/**
 * Show the original string of a Fluent entity.
 *
 * Based on the syntax type of the string, render it as a simple string preview,
 * as a rich UI or as the original, untouched string.
 */
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

    // Complex, unsupported strings.
    return <p className="original" onClick={ props.handleClickOnPlaceable }>
        <WithPlaceablesForFluent>
            { props.entity.original }
        </WithPlaceablesForFluent>
    </p>;
}
