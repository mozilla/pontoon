/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import { getMarker } from 'core/term';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locale';
import type { TermState } from 'core/term';

type Props = {|
    +entity: Entity,
    +locale: Locale,
    +pluralForm: number,
    +terms: TermState,
    +handleClickOnPlaceable: (
        SyntheticMouseEvent<HTMLParagraphElement>,
    ) => void,
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
            title: (
                <Localized id='entitydetails-GenericOriginalString--singular'>
                    <h2>SINGULAR</h2>
                </Localized>
            ),
            original: entity.original,
        };
    }

    return {
        title: (
            <Localized id='entitydetails-GenericOriginalString--plural'>
                <h2>PLURAL</h2>
            </Localized>
        ),
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

    const TermsAndPlaceablesMarker = getMarker(props.terms);

    return (
        <>
            {title}
            <p className='original' onClick={props.handleClickOnPlaceable}>
                <TermsAndPlaceablesMarker>{original}</TermsAndPlaceablesMarker>
            </p>
        </>
    );
}
