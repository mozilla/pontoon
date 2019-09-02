/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import { WithPlaceables } from 'core/placeable';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locale';


type Props = {|
    +entity: Entity,
    +locale: Locale,
    +pluralForm: number,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


function getOriginalContent(props: Props) {
    const { entity, locale, pluralForm } = props;

    if (pluralForm === -1) {
        return {
            title: null,
            original: entity.original,
        };
    }

    if (locale.cldrPlurals[pluralForm] === 1) {
        return {
            title: <Localized id='entitydetails-GenericOriginalString--singular'>
                <h2>Singular</h2>
            </Localized>,
            original: entity.original,
        };
    }

    return {
        title: <Localized id='entitydetails-GenericOriginalString--plural'>
            <h2>Plural</h2>
        </Localized>,
        original: entity.original_plural,
    };
}


/**
 * Show the original string of an entity.
 *
 * Based on the plural form, show either the singular or plural version of the
 * string, and also display which form is being rendered.
 */
export default function GenericOriginalString(props: Props) {
    const { title, original } = getOriginalContent(props);

    return <>
        { title }
        <p className="original" onClick={ props.handleClickOnPlaceable }>
            <WithPlaceables>
                { original }
            </WithPlaceables>
        </p>
    </>;
}
