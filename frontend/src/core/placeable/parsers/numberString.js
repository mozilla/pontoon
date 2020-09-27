/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks numbers.
 *
 * Example matches:
 *
 *   42
 *   42.0
 *   4,200.00
 *   4 200.00 (with no-break space)
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L72
 */
const numberString = {
    rule: /([-+]?[0-9]+([\u00A0.,][0-9]+)*)\b/u,
    matchIndex: 0,
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-numberString'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Number'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default numberString;
