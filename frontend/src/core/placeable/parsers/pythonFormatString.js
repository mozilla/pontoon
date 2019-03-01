/* @flow */

import * as React from 'react';


const pythonFormatString = {
    rule: /(\{{?[\w\d!.,[\]%:$<>+-= ]*\}?})/,
    tag: (x: string) => <mark className='placeable' title='Python format string'>
        { x }
    </mark>,
};

export default pythonFormatString;
