import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Microsoft Translation.
 */
export function MicrosoftTranslation(): React.ReactElement<'li'> {
  return (
    <li>
      <Localized
        id='machinery-MicrosoftTranslation--translation-source'
        attrs={{ title: true }}
      >
        <span className='translation-source'>MICROSOFT TRANSLATOR</span>
      </Localized>
    </li>
  );
}
