/* @flow */

import * as React from 'react';


/**
 * Marks terms following the CamelCase convention.
 *
 * Example matches:
 *
 *   CamelCase
 *   LongCamelCasedTerm
 *   iSomething
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L274
 */
const camelCaseString = {
    rule: /(\b([a-z]+[A-Z]|[A-Z]+[a-z]+[A-Z]|[A-Z]{2,}[a-z])[a-zA-Z0-9]*\b)/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Camel case string'>
        { x }
    </mark>,
};

export default camelCaseString;
