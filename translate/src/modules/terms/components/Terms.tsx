import { Localized } from '@fluent/react';
import React from 'react';

import { TermsList, TermState } from '~/core/term';

import './Terms.css';

type Props = {
  isReadOnlyEditor: boolean;
  terms: TermState;
  navigateToPath: (arg0: string) => void;
};

/**
 * Shows all terms found in the source string.
 */
export function Terms({
  isReadOnlyEditor,
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
        <TermsList
          isReadOnlyEditor={isReadOnlyEditor}
          navigateToPath={navigateToPath}
          terms={terms}
        />
      )}
    </section>
  );
}
