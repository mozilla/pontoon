import React, { useRef } from 'react';

import type { TermType } from '~/api/terminology';
import { TermsList } from '~/modules/terms';
import { useOnDiscard } from '~/utils';

import './TermsPopup.css';

type Props = {
  navigateToPath: (path: string) => void;
  onClick: () => void;
  terms: Array<TermType>;
};

/**
 * Shows a popup with a list of all terms belonging to the highlighted one.
 */
export function TermsPopup({
  navigateToPath,
  onClick,
  terms,
}: Props): React.ReactElement<'div'> {
  const ref = useRef(null);
  useOnDiscard(ref, onClick);
  return (
    <div ref={ref} className='terms-popup' onClick={onClick}>
      <TermsList navigateToPath={navigateToPath} terms={terms} />
    </div>
  );
}
