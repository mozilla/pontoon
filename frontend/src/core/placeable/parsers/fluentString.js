/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks string expressions from Fluent syntax.
 *
 * Documentation: https://projectfluent.org/fluent/guide/special.html#quoted-text
 *
 * Example matches:
 *
 *   { "" }
 *   { "Hello, World" }
 */
const fluentString = {
    rule: /({ ?"[^}]*" ?})/,
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-fluentString'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Fluent string expression'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default fluentString;
