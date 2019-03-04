/* @flow */

import * as React from 'react';


const numberString = {
    rule: /([-+]?[0-9]+([\u00A0.,][0-9]+)*)/u,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Number'>
        { x }
    </mark>,
};

export default numberString;
