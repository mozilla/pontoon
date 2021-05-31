import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks the tab character "\t".
 */
const tabCharacter = {
    rule: '\t',
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-tabCharacter'
                attrs={{ title: true }}
            >
                <mark
                    className='placeable'
                    title='Tab character'
                    data-match={x}
                >
                    &rarr;
                </mark>
            </Localized>
        );
    },
};

export default tabCharacter;
