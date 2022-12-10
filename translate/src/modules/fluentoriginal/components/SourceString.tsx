import React from 'react';

import type { Entity } from '~/api/entity';
import { Marked } from '~/core/placeable/components/Marked';
import type { TermState } from '~/core/term';

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
export function SourceString({
  entity,
  handleClickOnPlaceable,
  terms,
}: Props): React.ReactElement<'p'> {
  return (
    <p className='original' onClick={handleClickOnPlaceable}>
      <Marked fluent terms={terms}>
        {entity.original}
      </Marked>
    </p>
  );
}
