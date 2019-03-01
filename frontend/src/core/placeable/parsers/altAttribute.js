/* @flow */

import * as React from 'react';


const altAttribute = {
    rule: /(alt=".*?")/i,
    tag: (x: string) => <mark className='placeable' title="'alt' attribute inside XML tag">
        { x }
    </mark>,
};

export default altAttribute;
