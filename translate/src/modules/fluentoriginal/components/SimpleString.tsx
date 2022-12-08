import React from 'react';

import type { Entity } from '~/api/entity';
import { getMarker, TermState } from '~/core/term';
import { getSimplePreview } from '~/utils/fluent';

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
export function SimpleString(props: Props): React.ReactElement<'p'> {
  const original = getSimplePreview(props.entity.original);
  const TermsAndPlaceablesMarker = getMarker(props.terms, true);
  return (
    <p className='original' onClick={props.handleClickOnPlaceable}>
      <TermsAndPlaceablesMarker>{original}</TermsAndPlaceablesMarker>
    </p>
  );
}
