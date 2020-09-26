/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks multiple consecutive spaces and replaces them with a middle dot.
 */
const multipleSpaces = {
    rule: /(  +)/,
    tag: (x: string) => {
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
                    {' '}
                    &middot;{' '}
                </mark>
            </Localized>
        );
    },
};

export default multipleSpaces;
