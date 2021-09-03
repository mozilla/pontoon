import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks command line options.
 *
 * Example matches:
 *
 *   --help
 *   -i
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L317
 */
const optionPattern = {
    rule: /(\B(-[a-zA-Z]|--[a-z-]+)\b)/ as RegExp,
    matchIndex: 0,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-optionPattern'
                attrs={{ title: true }}
            >
                <mark className='placeable' title='Command line option'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default optionPattern;
