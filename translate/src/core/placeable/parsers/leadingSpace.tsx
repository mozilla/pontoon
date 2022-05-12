import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks spaces at the beginning of a string.
 *
 * Example matches:
 *
 *   " Hello, world"
 */
export const leadingSpace = {
  rule: /(^ +)/ as RegExp,
  tag: (x: string): React.ReactElement<React.ElementType> => {
    return (
      <Localized id='placeable-parser-leadingSpace' attrs={{ title: true }}>
        <mark className='placeable' title='Leading space' dir='ltr'>
          {x}
        </mark>
      </Localized>
    );
  },
};
