/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks escaped newline characters.
 */
const newlineEscape = {
    rule: '\\n',
    tag: (x: string): React.Element<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-newlineEscape'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Escaped newline'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default newlineEscape;
