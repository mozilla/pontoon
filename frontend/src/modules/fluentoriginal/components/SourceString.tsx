import * as React from 'react';

import { getMarker } from 'core/term';

import type { Entity } from 'core/api';
import type { TermState } from 'core/term';

type Props = {
    readonly entity: Entity;
    readonly terms: TermState;
    readonly handleClickOnPlaceable: (
        event: React.MouseEvent<HTMLParagraphElement>,
    ) => void;
};

/**
 * Show the source string of a Fluent entity.
 */
export default function SourceString(props: Props): React.ReactElement<'p'> {
    const TermsAndPlaceablesMarker = getMarker(props.terms);

    return (
        <p className='original' onClick={props.handleClickOnPlaceable}>
            <TermsAndPlaceablesMarker>
                {props.entity.original}
            </TermsAndPlaceablesMarker>
        </p>
    );
}
