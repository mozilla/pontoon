import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks term expressions from Fluent syntax.
 *
 * Documentation: https://projectfluent.org/fluent/guide/terms.html
 *
 * Example matches:
 *
 *   {-brand}
 *   { -brand }
 *   { -brand-name }
 */
const fluentTerm = {
    rule: /({ ?-[^}]* ?})/ as RegExp,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized id='placeable-parser-fluentTerm' attrs={{ title: true }}>
                <mark className='placeable' title='Fluent term'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default fluentTerm;
