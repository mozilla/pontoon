/* @flow */

import * as React from 'react';


const allCapitalsString = {
    rule: /(\b[A-Z][A-Z_/\-:*0-9]{1,}[A-Z0-9]\b[+]?)/,
    tag: (x: string) => <mark className='placeable' title='Long all-caps string'>
        { x }
    </mark>,
};

export default allCapitalsString;
