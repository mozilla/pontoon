import * as React from 'react';
import { Localized } from '@fluent/react';

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
    rule: /(alt=".*?")/i as RegExp,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-altAttribute'
                attrs={{ title: true }}
            >
                <mark
                    className='placeable'
                    title="'alt' attribute inside XML tag"
                >
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default altAttribute;
