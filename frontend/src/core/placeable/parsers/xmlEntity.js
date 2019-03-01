/* @flow */

import * as React from 'react';


const xmlEntity = {
    rule: /(&(([a-zA-Z][a-zA-Z0-9.-]*)|([#](\d{1,5}|x[a-fA-F0-9]{1,5})+));)/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='XML entity'>
        { x }
    </mark>,
};

export default xmlEntity;
