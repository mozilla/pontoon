import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks Python new string formatting variables.
 *
 * Documentation:
 * https://docs.python.org/3/library/string.html#formatstrings
 *
 * Example matches:
 *
 *   {0}
 *   {number}
 *   {foo[42]}
 */
export const pythonFormatString = {
  rule: /(\{{?[\w\d!.,[\]%:$<>+-= ]*\}?})/ as RegExp,
  tag: (x: string): React.ReactElement<React.ElementType> => {
    return (
      <Localized
        id='placeable-parser-pythonFormatString'
        attrs={{ title: true }}
      >
        <mark className='placeable' title='Python format string' dir='ltr'>
          {x}
        </mark>
      </Localized>
    );
  },
};
