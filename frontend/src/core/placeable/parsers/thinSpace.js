/* @flow */

import * as React from 'react';


const thinSpace = {
    rule: /([\u2009])/,
    tag: (x: string) => <mark className='placeable' title='Thin space'>{ x }</mark>,
};

export default thinSpace;
