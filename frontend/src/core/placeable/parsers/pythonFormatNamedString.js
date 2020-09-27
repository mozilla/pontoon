/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks Python formatting named variables.
 *
 * Example matches:
 *
 *   %(name)s
 *   %(number)D
 */
const pythonFormatNamedString = {
    rule: /(%\([[\w\d!.,[\]%:$<>+\-= ]*\)[+|-|0\d+|#]?[.\d+]?[s|d|e|f|g|o|x|c|%])/i,
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-pythonFormatNamedString'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Python format string'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default pythonFormatNamedString;
