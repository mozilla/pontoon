/* @flow */

import * as React from 'react';


/**
 * Marks `alt` attributes and their values inside XML tags.
 *
 * Example matches:
 *
 *   alt="image description"
 *   ALT=""
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L55
 */
const altAttribute = {
    rule: /(alt=".*?")/i,
    tag: (x: string) => <mark className='placeable' title="'alt' attribute inside XML tag">
        { x }
    </mark>,
};

export default altAttribute;
