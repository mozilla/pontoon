/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';


/**
 * Marks the tab character "\t".
 */
const tabCharacter = {
    rule: '\t',
    tag: () => {
        return <Localized
            id='placeable-parser-tabCharacter'
            attrs={{ title: true }}
        >
            <mark className='placeable' title='Tab character'>
                &rarr;
            </mark>
        </Localized>;
    },
};

export default tabCharacter;
