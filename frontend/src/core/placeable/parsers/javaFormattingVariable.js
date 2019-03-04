/* @flow */

import * as React from 'react';


const javaFormattingVariable = {
    rule: /({[0-9]+(,\s*(number(,\s*(integer|currency|percent|[-0#.,E;%\u2030\u00a4']+)?)?|(date|time)(,\s*(short|medium|long|full|.+?))?|choice,([^{]+({.+})?)+)?)?})/,
    matchIndex: 0,
    tag: (x: string) => <mark className='placeable' title='Java Message formatting variable'>
        { x }
    </mark>,
};

export default javaFormattingVariable;
