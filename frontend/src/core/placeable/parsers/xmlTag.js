/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks XML tags.
 *
 * Example matches:
 *
 *   <user>
 *   </user>
 *   <tag attr="foo" />
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L301
 */
const xmlTag = {
    rule: /(<[\w.:]+(\s([\w.:-]+=((".*?")|('.*?')))?)*\/?>|<\/[\w.]+>)/,
    matchIndex: 0,
    tag: (x: string) => {
        return (
            <Localized id='placeable-parser-xmlTag' attrs={{ title: true }}>
                <mark className='placeable' title='XML tag'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default xmlTag;
