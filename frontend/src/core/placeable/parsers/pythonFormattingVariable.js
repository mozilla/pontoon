/* @flow */

import * as React from 'react';


const pythonFormattingVariable = {
    rule: /(%(%|(\([^)]+\)){0,1}[-+0\s#]{0,1}(\d+|\*){0,1}(\.(\d+|\*)){0,1}[hlL]{0,1}[diouxXeEfFgGcrs]{1}))/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='XML entity'>
        { x }
    </mark>,
};

export default pythonFormattingVariable;
