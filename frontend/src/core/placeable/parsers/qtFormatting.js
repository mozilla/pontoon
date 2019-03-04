/* @flow */

import * as React from 'react';


const qtFormatting = {
    rule: /(%L?[1-9]\d{0,1}(?=([^\d]|$)))/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Qt string formatting variable'>
        { x }
    </mark>,
};

export default qtFormatting;
