/* @flow */

import * as React from 'react';


/**
 * Marks the tab character "\t".
 */
const tabCharacter = {
    rule: '\t',
    tag: () => <mark className='placeable' title='Tab character'>
        &rarr;
    </mark>,
};

export default tabCharacter;
