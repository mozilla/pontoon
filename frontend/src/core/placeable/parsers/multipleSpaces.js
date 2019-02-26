/* @flow */

import * as React from 'react';


const multipleSpaces = {
    rule: /(  +)/gi,
    tag: () => <mark className='placeable' title='Multiple spaces'>
        { ' ' }&middot;{ ' ' }
    </mark>,
};

export default multipleSpaces;
