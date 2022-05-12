import React from 'react';

import type { Entity } from '~/api/entity';
import { getMarker, TermState } from '~/core/term';

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
export function SourceString(props: Props): React.ReactElement<'p'> {
  const TermsAndPlaceablesMarker = getMarker(props.terms, true);

  return (
    <p className='original' onClick={props.handleClickOnPlaceable}>
      <TermsAndPlaceablesMarker>
        {props.entity.original}
      </TermsAndPlaceablesMarker>
    </p>
  );
}
