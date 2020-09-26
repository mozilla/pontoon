/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks the thin space character (Unicode U+2009).
 */
const thinSpace = {
    rule: /([\u2009])/,
    tag: (x: string) => {
        return (
            <Localized id='placeable-parser-thinSpace' attrs={{ title: true }}>
                <mark className='placeable' title='Thin space'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default thinSpace;
