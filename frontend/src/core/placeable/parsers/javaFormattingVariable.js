/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks Java MessageFormat formatting variables.
 *
 * Implemented according to the Java MessageFormat documentation —
 * https://docs.oracle.com/javase/7/docs/api/java/text/MessageFormat.html
 *
 * Information about custom formats:
 *   - number: DecimalFormat — https://docs.oracle.com/javase/7/docs/api/java/text/DecimalFormat.html
 *   - date/time: SimpleDateFormat — https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html
 *   - choice: ChoiceFormat — https://docs.oracle.com/javase/7/docs/api/java/text/ChoiceFormat.html
 *
 * Example matches:
 *
 *   {2}
 *   {1,date}
 *   {0,number,integer}
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L127
 */
const javaFormattingVariable = {
    rule: /({[0-9]+(,\s*(number(,\s*(integer|currency|percent|[-0#.,E;%\u2030\u00a4']+)?)?|(date|time)(,\s*(short|medium|long|full|.+?))?|choice,([^{]+({.+})?)+)?)?})/,
    matchIndex: 0,
    tag: (x: string) => {
        return (
            <Localized
                id='placeable-parser-javaFormattingVariable'
                attrs={{ title: true }}
            >
                <mark
                    className='placeable'
                    title='Java Message formatting variable'
                >
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default javaFormattingVariable;
