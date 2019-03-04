/* @flow */

import * as React from 'react';


const newlineEscape = {
    rule: '\\n',
    tag: (x: string) => <mark className='placeable' title='Escaped newline'>
        { x }
    </mark>,
};

export default newlineEscape;
