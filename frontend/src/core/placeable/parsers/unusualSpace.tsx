import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks unusually placed spaces:
 * - at the end of a line
 * - after a newline or tab
 * - multiple spaces
 *
 * Example matches:
 *
 *   "hello world "
 *   "hello\t world"
 *   "hello  world"
 */
const unusualSpace = {
    rule: /( +$|[\r\n\t]( +)| {2,})/ as RegExp,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-unusualSpace'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Unusual space'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default unusualSpace;
