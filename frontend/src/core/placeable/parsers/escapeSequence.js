/* @flow */

import * as React from 'react';


/**
 * Marks the escape character "\".
 */
const escapeSequence = {
    rule: '\\',
    tag: (x: string) => <mark className='placeable' title='Escape sequence'>
        { x }
    </mark>,
};

export default escapeSequence;
