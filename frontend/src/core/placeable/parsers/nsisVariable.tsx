import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks NSIS variables.
 *
 * Example matches:
 *
 *   $Brand
 *   $BrandShortName
 */
const nsisVariable = {
    rule: /(^|\s)(\$[a-zA-Z][\w]*)/ as RegExp,
    matchIndex: 2,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-nsisVariable'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='NSIS variable'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default nsisVariable;
