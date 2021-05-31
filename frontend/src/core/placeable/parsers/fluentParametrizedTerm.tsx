import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks parametrized term expressions from Fluent syntax.
 *
 * Documentation: https://projectfluent.org/fluent/guide/terms.html#parameterized-terms
 *
 * Example matches:
 *
 *   {-brand(case: "test")}
 *   { -brand(case: "what ever") }
 *   { -brand-name(foo-bar: "now that's a value!") }
 */
const fluentParametrizedTerm = {
    rule: /({ ?-[^}]*([^}]*: ?[^}]*) ?})/ as RegExp,
    matchIndex: 1,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-fluentParametrizedTerm'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Fluent parametrized term'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default fluentParametrizedTerm;
