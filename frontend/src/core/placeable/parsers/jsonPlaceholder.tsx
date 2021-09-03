import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks JSON format placeholders as used by the WebExtension API.
 *
 * Terms must start and end with a dollar sign "$" and contain only capital
 * letters or underscores.
 *
 * Example matches:
 *
 *   $USER$
 *   $FIRST_NAME$
 */
const jsonPlaceholder = {
    rule: /(\$[A-Z0-9_]+\$)/ as RegExp,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-jsonPlaceholder'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='JSON placeholder'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default jsonPlaceholder;
