/* @flow */

import * as React from 'react';


/**
 * Marks the narrow no-break space character (Unicode U+202F).
 */
const narrowNonBreakingSpace = {
    rule: /([\u202F])/,
    tag: (x: string) => <mark className='placeable' title='Narrow non-breaking space'>
        { x }
    </mark>,
};

export default narrowNonBreakingSpace;
