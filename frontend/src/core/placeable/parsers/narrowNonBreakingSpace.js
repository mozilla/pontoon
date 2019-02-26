/* @flow */

import * as React from 'react';


const narrowNonBreakingSpace = {
    rule: /([\u202F])/gi,
    tag: (x: string) => <mark className='placeable' title='Narrow non-breaking space'>
        { x }
    </mark>,
};

export default narrowNonBreakingSpace;
