import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Google Translate.
 */
export function GoogleTranslation(): React.ReactElement<'li'> {
  return (
    <li className='google-translation'>
      <Localized id='machinery-GoogleTranslation--translation-source'>
        <span className='translation-source'>GOOGLE TRANSLATE</span>
      </Localized>
    </li>
  );
}
