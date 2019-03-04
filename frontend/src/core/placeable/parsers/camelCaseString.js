/* @flow */

import * as React from 'react';


const camelCaseString = {
    rule: /(\b([a-z]+[A-Z]|[A-Z]+[a-z]+[A-Z]|[A-Z]{2,}[a-z])[a-zA-Z0-9]*\b)/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Camel case string'>
        { x }
    </mark>,
};

export default camelCaseString;
