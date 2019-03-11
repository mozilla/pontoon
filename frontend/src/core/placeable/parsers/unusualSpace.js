/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';


/**
 * Marks unusually places spaces: at the beginning or end of a string,
 * after a newline or tab, or multiple spaces.
 *
 * Example matches:
 *
 *   " Hello, world"
 *   "Hellow, world "
 *   "Hello\t world"
 */
const unusualSpace = {
    rule: /(^ +| +$|[\r\n\t]( +)| {2,})/,
    tag: (x: string) => {
        return <Localized
            id='placeable-parser-unusualSpace'
            attrs={{ title: true }}
        >
            <mark className='placeable' title='Unusual space in string'>
                { x }
            </mark>
        </Localized>;
    },
};

export default unusualSpace;
