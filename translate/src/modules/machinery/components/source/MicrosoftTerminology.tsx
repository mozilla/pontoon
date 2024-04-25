import { Localized } from '@fluent/react';
import React from 'react';

/**
 * Show the translation source from Microsoft Terminology.
 */
export function MicrosoftTerminology(): React.ReactElement<'li'> {
  return (
    <li>
      <Localized id='machinery-MicrosoftTerminology--translation-source'>
        <span className='translation-source'>MICROSOFT</span>
      </Localized>
    </li>
  );
}
