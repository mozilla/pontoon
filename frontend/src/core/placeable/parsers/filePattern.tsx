import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks terms that look like a path to a folder or a file.
 *
 * Example matches:
 *
 *   /home/lisa
 *   /home/homer/budget.md
 *   ~/recipies.txt
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L208
 */
const filePattern = {
    rule: /(^|\s)((~\/|\/|\.\/)([-A-Za-z0-9_$.+!*(),;:@&=?/~#%]|\\){3,})/ as RegExp,
    matchIndex: 2,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-filePattern'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='File location'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default filePattern;
