import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks functions from Fluent syntax.
 *
 * Documentation: https://projectfluent.org/fluent/guide/functions.html
 *
 * Example matches:
 *
 *   {COPY()}
 *   { DATETIME($date) }
 *   { NUMBER($ratio, minimumFractionDigits: 2) }
 */
const fluentFunction = {
    rule: /({ ?[A-W0-9\-_]+[^}]* ?})/ as RegExp,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-fluentFunction'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Fluent function'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default fluentFunction;
