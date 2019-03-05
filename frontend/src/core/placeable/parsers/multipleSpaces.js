/* @flow */

import * as React from 'react';


/**
 * Marks multiple consecutive spaces and replaces them with a middle dot.
 */
const multipleSpaces = {
    rule: /(  +)/,
    tag: () => <mark className='placeable' title='Multiple spaces'>
        { ' ' }&middot;{ ' ' }
    </mark>,
};

export default multipleSpaces;
