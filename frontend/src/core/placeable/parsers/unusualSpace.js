/* @flow */

import * as React from 'react';


const unusualSpace = {
    rule: /(^ +| +$|[\r\n\t]( +)| {2,})/gi,
    tag: (x: string) => <mark className='placeable' title='Unusual space in string'>
        { x }
    </mark>,
};

export default unusualSpace;
