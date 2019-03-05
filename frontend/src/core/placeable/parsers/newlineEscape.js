/* @flow */

import * as React from 'react';


/**
 * Marks escaped newline characters.
 */
const newlineEscape = {
    rule: '\\n',
    tag: (x: string) => <mark className='placeable' title='Escaped newline'>
        { x }
    </mark>,
};

export default newlineEscape;
