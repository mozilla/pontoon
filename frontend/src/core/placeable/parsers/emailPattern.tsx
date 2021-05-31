import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks terms that look like an email address. Includes an eventual
 * "mailto:" scheme if found.
 *
 * Example matches:
 *
 *   lisa@example.org
 *   mailto:USER@example.me
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L220
 */
const emailPattern = {
    rule: /(((mailto:)|)[A-Za-z0-9]+[-a-zA-Z0-9._%]*@(([-A-Za-z0-9]+)\.)+[a-zA-Z]{2,4})/ as RegExp,
    matchIndex: 0,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-emailPattern'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Email'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default emailPattern;
