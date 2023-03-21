import { Localized } from '@fluent/react';
import React from 'react';

import type { TermState } from '../reducer';
import { TermsList } from './TermsList';

import './Terms.css';

type Props = {
  navigateToPath: (arg0: string) => void;
  terms: TermState;
};

/**
 * Shows all terms found in the source string.
 */
export function Terms({
  navigateToPath,
  terms: { fetching, terms },
}: Props): null | React.ReactElement<'section'> {
  return fetching || !terms ? null : (
    <section className='terms'>
      {!terms.length ? (
        <Localized id='entitydetails-Helpers--no-terms'>
          <p className='no-terms'>No terms available.</p>
        </Localized>
      ) : (
        <TermsList navigateToPath={navigateToPath} terms={terms} />
      )}
    </section>
  );
}
