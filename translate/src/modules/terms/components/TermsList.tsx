import React from 'react';

import type { TermType } from '~/api/terminology';

import { Term } from './Term';
import './TermsList.css';

type Props = {
  navigateToPath: (arg0: string) => void;
  terms: Array<TermType>;
};

/**
 * Shows a list of terms.
 */
export function TermsList({
  navigateToPath,
  terms,
}: Props): React.ReactElement<'ul'> {
  return (
    <ul className='terms-list'>
      {terms.map((term, i) => (
        <Term key={i} term={term} navigateToPath={navigateToPath} />
      ))}
    </ul>
  );
}
