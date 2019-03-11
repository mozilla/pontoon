/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';


/**
 * Marks the newline character "\n".
 */
const newlineCharacter = {
    rule: '\n',
    tag: () => {
        return <Localized
            id='placeable-parser-newlineCharacter'
            attrs={{ title: true }}
        >
            <mark className='placeable' title='Newline character'>
                { '¶\n' }
            </mark>
        </Localized>;
    },
};

export default newlineCharacter;
