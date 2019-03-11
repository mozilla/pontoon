/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';


/**
 * Marks multiple consecutive spaces and replaces them with a middle dot.
 */
const multipleSpaces = {
    rule: /(  +)/,
    tag: () => {
        return <Localized
            id='placeable-parser-multipleSpaces'
            attrs={{ title: true }}
        >
            <mark className='placeable' title='Multiple spaces'>
                { ' ' }&middot;{ ' ' }
            </mark>
        </Localized>;
    },
};

export default multipleSpaces;
