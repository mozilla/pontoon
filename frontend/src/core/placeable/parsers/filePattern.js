/* @flow */

import * as React from 'react';


const filePattern = {
    rule: /((~\/|\/|\.\/)([-A-Za-z0-9_$.+!*(),;:@&=?/~#%]|\\){3,})/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='File location'>
        { x }
    </mark>,
};

export default filePattern;
