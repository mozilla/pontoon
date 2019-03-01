/* @flow */

import * as React from 'react';


const xmlTag = {
    rule: /(<[\w.:]+(\s([\w.:]+=((".*?")|('.*?')))?)*\/?>|<\/[\w.]+>)/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='XML tag'>
        { x }
    </mark>,
};

export default xmlTag;
