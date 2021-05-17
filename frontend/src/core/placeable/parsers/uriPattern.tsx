import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks terms that look like a URI.
 *
 * Example matches:
 *
 *   https://example.org
 *   www.example.org/resource/42
 *   ftp://example.org/
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L192
 */
const uriPattern = {
    rule: new RegExp(
        '(' +
            '(' +
            '(' +
            /((news|nttp|file|https?|ftp|irc):\/\/)/.source + // has to start with a protocol
            /|((www|ftp)[-A-Za-z0-9]*\.)/.source + // or www... or ftp... hostname
            ')' +
            /([-A-Za-z0-9]+(\.[-A-Za-z0-9]+)*)/.source + // hostname
            /|(\d{1,3}(\.\d{1,3}){3,3})/.source + // or IP address
            ')' +
            /(:[0-9]{1,5})?/.source + // optional port
            /(\/[a-zA-Z0-9-_$.+!*(),;:@&=?/~#%]*)?/.source + // optional trailing path
            /(?=$|\s|([\]'}>),"]))/.source +
            ')',
        'i', // This one is not case sensitive.
    ) as RegExp,
    matchIndex: 0,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized id='placeable-parser-uriPattern' attrs={{ title: true }}>
                <mark className='placeable' title='URI'>
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default uriPattern;
