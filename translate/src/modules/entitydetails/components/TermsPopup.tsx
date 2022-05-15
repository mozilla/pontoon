import React, { useRef } from 'react';

import type { TermType } from '~/api/terminology';
import { TermsList } from '~/core/term';
import { useOnDiscard } from '~/core/utils';

import './TermsPopup.css';

type Props = {
  readonly isReadOnlyEditor: boolean;
  readonly terms: Array<TermType>;
  readonly hide: () => void;
  readonly navigateToPath: (path: string) => void;
};

/**
 * Shows a popup with a list of all terms belonging to the highlighted one.
 */
export function TermsPopup({
  hide,
  ...props
}: Props): React.ReactElement<'div'> {
  const ref = useRef(null);
  useOnDiscard(ref, hide);
  return (
    <div ref={ref} className='terms-popup' onClick={hide}>
      <TermsList {...props} />
    </div>
  );
}
