/* @flow */

import * as React from 'react';


const multipleSpaces = {
    rule: /(  +)/,
    tag: () => <mark className='placeable' title='Multiple spaces'>
        { ' ' }&middot;{ ' ' }
    </mark>,
};

export default multipleSpaces;
