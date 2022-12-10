import React from 'react';

import type { Entity } from '~/api/entity';
import { Marked } from '~/core/placeable/components/Marked';
import type { TermState } from '~/core/term';
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
  return (
    <p className='original' onClick={handleClickOnPlaceable}>
      <Marked fluent terms={terms}>
        {plain}
      </Marked>
    </p>
  );
}
