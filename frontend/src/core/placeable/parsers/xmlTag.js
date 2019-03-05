/* @flow */

import * as React from 'react';


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
    rule: /(<[\w.:]+(\s([\w.:]+=((".*?")|('.*?')))?)*\/?>|<\/[\w.]+>)/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='XML tag'>
        { x }
    </mark>,
};

export default xmlTag;
