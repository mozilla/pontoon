/* @flow */

import * as React from 'react';


/**
 * Marks the newline character "\n".
 */
const newlineCharacter = {
    rule: '\n',
    tag: () => <mark className='placeable' title='Newline character'>
        { '¶\n' }
    </mark>,
};

export default newlineCharacter;
