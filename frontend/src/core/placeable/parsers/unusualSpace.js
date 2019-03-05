/* @flow */

import * as React from 'react';


/**
 * Marks unusually places spaces: at the beginning or end of a string,
 * after a newline or tab, or multiple spaces.
 *
 * Example matches:
 *
 *   " Hello, world"
 *   "Hellow, world "
 *   "Hello\t world"
 */
const unusualSpace = {
    rule: /(^ +| +$|[\r\n\t]( +)| {2,})/,
    tag: (x: string) => <mark className='placeable' title='Unusual space in string'>
        { x }
    </mark>,
};

export default unusualSpace;
