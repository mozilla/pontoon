import React from 'react';

import type { Entity } from '~/api/entity';
import { getMarker, TermState } from '~/core/term';
import { getPlainMessage } from '~/utils/message';

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
export function SimpleString({
  entity,
  handleClickOnPlaceable,
  terms,
}: Props): React.ReactElement<'p'> {
  const plain = getPlainMessage(entity.original, entity.format);
  const TermsAndPlaceablesMarker = getMarker(terms, true);
  return (
    <p className='original' onClick={handleClickOnPlaceable}>
      <TermsAndPlaceablesMarker>{plain}</TermsAndPlaceablesMarker>
    </p>
  );
}
