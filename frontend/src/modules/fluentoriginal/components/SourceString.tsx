import * as React from 'react';

import { getMarker } from 'core/term';

import { Entity } from 'core/api';
import { TermState } from 'core/term';

type Props = {
    readonly entity: Entity;
    readonly terms: TermState;
    readonly handleClickOnPlaceable: (
        arg0: React.MouseEvent<HTMLParagraphElement>,
    ) => void;
};

/**
 * Show the source string of a Fluent entity.
 */
export default function SourceString(props: Props) {
    const TermsAndPlaceablesMarker = getMarker(props.terms);

    return (
        <p className='original' onClick={props.handleClickOnPlaceable}>
            <TermsAndPlaceablesMarker>
                {props.entity.original}
            </TermsAndPlaceablesMarker>
        </p>
    );
}
