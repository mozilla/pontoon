/* @flow */

import * as React from 'react';


const stringFormattingVariable = {
    rule: /(%(\d+\$)?[-+0 #'I]?((\d+)|[*])?(\.\d+)?[hlI]?[cCdiouxXeEfgGnpsS])/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='String formatting variable'>
        { x }
    </mark>,
};

export default stringFormattingVariable;
