/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks printf string formatting variables.
 *
 * See `man 3 printf` for documentation. Not everything is supported.
 *
 * Example matches:
 *
 *   %d
 *   %Id
 *   %33d
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L154
 */
const stringFormattingVariable = {
    rule: /(%(\d+\$)?[-+0#'I]?((\d+)|[*])?(\.\d+)?[hlI]?[cCdiouxXeEfgGnpsS])/,
    matchIndex: 0,
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-stringFormattingVariable'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='String formatting variable'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default stringFormattingVariable;
