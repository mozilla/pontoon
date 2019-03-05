/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';


/**
 * Marks terms at least 2-letters-long containing only capital letters
 * and some special characters.
 *
 * Example matches:
 *
 *   USER
 *   HELLO_WORLD
 *   MYWORD:8+
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L266
 */
const allCapitalsString = {
    rule: /(\b[A-Z][A-Z_/\-:*0-9]{1,}[A-Z0-9]\b[+]?)/,
    tag: (x: string) => {
        return <Localized
            id='placeable-parser-allCapitalsString'
            attrs={{ title: true }}
        >
            <mark className='placeable' title='Long all-caps string'>
                { x }
            </mark>
        </Localized>;
    },
};

export default allCapitalsString;
