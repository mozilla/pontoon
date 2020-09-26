/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks the escape character "\".
 */
const escapeSequence = {
    rule: '\\',
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-escapeSequence'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Escape sequence'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default escapeSequence;
