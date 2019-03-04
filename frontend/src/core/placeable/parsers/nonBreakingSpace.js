/* @flow */

import * as React from 'react';


const nonBreakingSpace = {
    rule: '\u00A0',
    tag: (x: string) => <mark className='placeable' title='Non-breaking space'>
        { x }
    </mark>,
};

export default nonBreakingSpace;
