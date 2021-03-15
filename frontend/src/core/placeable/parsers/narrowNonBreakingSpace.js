/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks the narrow no-break space character (Unicode U+202F).
 */
const narrowNonBreakingSpace = {
    rule: (/([\u202F])/: RegExp),
    tag: (x: string): React.Element<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-narrowNonBreakingSpace'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Narrow non-breaking space'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default narrowNonBreakingSpace;
