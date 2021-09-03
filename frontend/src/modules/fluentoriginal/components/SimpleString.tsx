import * as React from 'react';

import { getMarker } from 'core/term';
import { fluent } from 'core/utils';

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
 * Show the original string of a Fluent entity as a simple preview.
 */
export default function SimpleString(props: Props): React.ReactElement<'p'> {
    const original = fluent.getSimplePreview(props.entity.original);
    const TermsAndPlaceablesMarker = getMarker(props.terms);
    return (
        <p className='original' onClick={props.handleClickOnPlaceable}>
            <TermsAndPlaceablesMarker>{original}</TermsAndPlaceablesMarker>
        </p>
    );
}
