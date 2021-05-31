import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks the newline character "\n".
 */
const newlineCharacter = {
    rule: '\n',
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-newlineCharacter'
                attrs={{ title: true }}
            >
                <mark
                    className='placeable'
                    title='Newline character'
                    data-match={x}
                >
                    {'¶\n'}
                </mark>
            </Localized>
        );
    },
};

export default newlineCharacter;
