/* @flow */

import * as React from 'react';


const newlineCharacter = {
    rule: '\n',
    tag: () => <mark className='placeable' title='Newline character'>
        { '¶\n' }
    </mark>,
};

export default newlineCharacter;
