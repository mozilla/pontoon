/* @flow */

import * as React from 'react';


const punctuation = {
    rule: new RegExp(
        '('
        + '('
        + /[™©®]|/.source // Marks
        + /[℃℉°]|/.source // Degree related
        + /[±πθ×÷−√∞∆Σ′″]|/.source // Maths
        + /[‘’ʼ‚‛“”„‟]|/.source // Quote characters
        + /[«»]|/.source // Guillemets
        + /[£¥€]|/.source // Currencies
        + /…|/.source // U2026 - horizontal ellipsis
        + /—|/.source // U2014 - em dash
        + /–|/.source // U2013 - en dash
        + /[\u202F]/.source // U202F - narrow no-break space
        + ')+'
        + ')'
    ),
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Punctuation'>
        { x }
    </mark>,
};

export default punctuation;
