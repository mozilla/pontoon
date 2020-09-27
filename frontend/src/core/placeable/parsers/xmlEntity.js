/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks XML entities.
 *
 * Example matches:
 *
 *   &brandShortName;
 *   &#1234;
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L254
 */
const xmlEntity = {
    rule: /(&(([a-zA-Z][a-zA-Z0-9.-]*)|([#](\d{1,5}|x[a-fA-F0-9]{1,5})+));)/,
    matchIndex: 0,
    tag: (x: string) => {
        return (
            <Localized id='placeable-parser-xmlEntity' attrs={{ title: true }}>
                <mark className='placeable' title='XML entity'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default xmlEntity;
