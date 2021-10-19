import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks multiple consecutive spaces and replaces them with a middle dot.
 */
const multipleSpaces = {
    rule: /(  +)/ as RegExp,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-multipleSpaces'
                attrs={{ title: true }}
            >
                <mark
                    className='placeable'
                    title='Multiple spaces'
                    data-match={x}
                >
                    <span style={{ display: 'inline-block', width: 0 }}>
                        {x}
                    </span>
                    <span style={{ userSelect: 'none' }}> &middot; </span>
                </mark>
            </Localized>
        );
    },
};

export default multipleSpaces;
