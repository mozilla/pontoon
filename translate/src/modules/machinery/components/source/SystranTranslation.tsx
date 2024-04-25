import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Systran.
 */
export function SystranTranslation(): React.ReactElement<'li'> {
  return (
    <li>
      <Localized id='machinery-SystranTranslation--translation-source'>
        <span className='translation-source'>SYSTRAN TRANSLATE</span>
      </Localized>
    </li>
  );
}
