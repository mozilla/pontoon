/* @flow */

import * as React from 'react';


const emailPattern = {
    rule: /(((mailto:)|)[A-Za-z0-9]+[-a-zA-Z0-9._%]*@(([-A-Za-z0-9]+)\.)+[a-zA-Z]{2,4})/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Email'>
        { x }
    </mark>,
};

export default emailPattern;
