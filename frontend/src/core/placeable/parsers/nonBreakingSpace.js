/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks the no-break space character (Unicode U+00A0).
 */
const nonBreakingSpace = {
    rule: '\u00A0',
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-nonBreakingSpace'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Non-breaking space'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default nonBreakingSpace;
