import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks spaces at the beginning of a string.
 *
 * Example matches:
 *
 *   " Hello, world"
 */
const leadingSpace = {
    rule: /(^ +)/ as RegExp,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-leadingSpace'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Leading space'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default leadingSpace;
