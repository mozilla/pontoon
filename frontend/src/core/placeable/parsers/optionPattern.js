/* @flow */

import * as React from 'react';


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
    rule: /(\B(-[a-zA-Z]|--[a-z-]+)\b)/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Command line option'>
        { x }
    </mark>,
};

export default optionPattern;
