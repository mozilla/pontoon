import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks 2-letters-long terms containing a combination of a capital letter and
 * a number.
 *
 * Example matches:
 *
 *   3D
 *   A4
 */
export const shortCapitalNumberString = {
  rule: /(\b([A-Z][0-9])|([0-9][A-Z])\b)/ as RegExp,
  tag: (x: string): React.ReactElement<React.ElementType> => {
    return (
      <Localized
        id='placeable-parser-shortCapitalNumberString'
        attrs={{ title: true }}
      >
        <mark
          className='placeable'
          title='Short capital letter and number string'
          dir='ltr'
        >
          {x}
        </mark>
      </Localized>
    );
  },
};
