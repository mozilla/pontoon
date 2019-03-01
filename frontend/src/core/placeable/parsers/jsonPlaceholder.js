/* @flow */

import * as React from 'react';


const jsonPlaceholder = {
    rule: /(\$[A-Z0-9_]+\$)/,
    tag: (x: string) => <mark className='placeable' title='JSON placeholder'>
        { x }
    </mark>,
};

export default jsonPlaceholder;
