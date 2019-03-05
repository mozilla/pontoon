/* @flow */

import * as React from 'react';


/**
 * Marks the no-break space character (Unicode U+00A0).
 */
const nonBreakingSpace = {
    rule: '\u00A0',
    tag: (x: string) => <mark className='placeable' title='Non-breaking space'>
        { x }
    </mark>,
};

export default nonBreakingSpace;
