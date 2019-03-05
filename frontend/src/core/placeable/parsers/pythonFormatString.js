/* @flow */

import * as React from 'react';


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
const pythonFormatString = {
    rule: /(\{{?[\w\d!.,[\]%:$<>+-= ]*\}?})/,
    tag: (x: string) => <mark className='placeable' title='Python format string'>
        { x }
    </mark>,
};

export default pythonFormatString;
