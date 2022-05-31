import React from 'react';

import type { TermType } from '~/api/terminology';

import { Term } from './Term';
import './TermsList.css';

type Props = {
  isReadOnlyEditor: boolean;
  terms: Array<TermType>;
  navigateToPath: (arg0: string) => void;
};

/**
 * Shows a list of terms.
 */
export function TermsList({
  isReadOnlyEditor,
  navigateToPath,
  terms,
}: Props): React.ReactElement<'ul'> {
  return (
    <ul className='terms-list'>
      {terms.map((term, i) => {
        return (
          <Term
            key={i}
            isReadOnlyEditor={isReadOnlyEditor}
            term={term}
            navigateToPath={navigateToPath}
          />
        );
      })}
    </ul>
  );
}
