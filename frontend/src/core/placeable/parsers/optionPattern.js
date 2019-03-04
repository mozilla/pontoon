/* @flow */

import * as React from 'react';


const optionPattern = {
    rule: /(\B(-[a-zA-Z]|--[a-z-]+)\b)/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Command line option'>
        { x }
    </mark>,
};

export default optionPattern;
