/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks Qt string formatting variables.
 *
 * Implemented following Qt documentation on QString::arg:
 * https://doc.qt.io/qt-5/qstring.html#arg
 * The placeables are refered to as 'place markers'.
 *
 * Notes:
 *   - Place markers can be reordered
 *   - Place markers may be repeated
 *   - 'L' use a localised representation e.g. in a number
 *   - %% some in the wild to escape real %, not documented (not in regex)
 *
 * Example matches:
 *
 *   %1
 *   %99
 *   %L1
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L80
 */
const qtFormatting = {
    rule: /(%L?[1-9]\d{0,1}(?=([^\d]|$)))/,
    matchIndex: 0,
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-qtFormatting'
                attrs={{ title: true }}
            >
                <mark
                    className='placeable'
                    title='Qt string formatting variable'
                >
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default qtFormatting;
