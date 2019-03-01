/* @flow */

import * as React from 'react';


const pythonFormatNamedString = {
    rule: /(%\([[\w\d!.,[\]%:$<>+\-= ]*\)[+|-|0\d+|#]?[.\d+]?[s|d|e|f|g|o|x|c|%])/i,
    tag: (x: string) => <mark className='placeable' title='Python format string'>
        { x }
    </mark>,
};

export default pythonFormatNamedString;
