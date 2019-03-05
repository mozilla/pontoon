/* @flow */

import * as React from 'react';


/**
 * Marks the thin space character (Unicode U+2009).
 */
const thinSpace = {
    rule: /([\u2009])/,
    tag: (x: string) => <mark className='placeable' title='Thin space'>{ x }</mark>,
};

export default thinSpace;
