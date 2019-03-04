/* @flow */

import * as React from 'react';


const uriPattern = {
    rule: new RegExp('('
        + '('
        + '('
        + /((news|nttp|file|https?|ftp|irc):\/\/)/.source // has to start with a protocol
        + /|((www|ftp)[-A-Za-z0-9]*\.)/.source // or www... or ftp... hostname
        + ')'
        + /([-A-Za-z0-9]+(\.[-A-Za-z0-9]+)*)/.source // hostname
        + /|(\d{1,3}(\.\d{1,3}){3,3})/.source // or IP address
        + ')'
        + /(:[0-9]{1,5})?/.source // optional port
        + /(\/[a-zA-Z0-9-_$.+!*(),;:@&=?/~#%]*)?/.source // optional trailing path
        + /(?=$|\s|([\]'}>),"]))/.source
        + ')',
        'i' // This one is not case sensitive.
    ),
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='URI'>
        { x }
    </mark>,
};

export default uriPattern;
