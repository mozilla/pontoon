import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Caighdean Machine Translation.
 */
export function CaighdeanTranslation(): React.ReactElement<'li'> {
  return (
    <li>
      <Localized id='machinery-CaighdeanTranslation--translation-source'>
        <span className='translation-source'>CAIGHDEAN</span>
      </Localized>
    </li>
  );
}
