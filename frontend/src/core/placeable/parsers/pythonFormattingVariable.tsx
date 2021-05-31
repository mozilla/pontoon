import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Marks Python string formatting variables.
 *
 * Implemented following Python documentation on String Formatting Operations:
 * https://docs.python.org/2/library/stdtypes.html#string-formatting
 *
 * Example matches:
 *
 *   %s
 *   %(tag)d
 *   %(number)3.1d
 *
 * Source:
 * https://github.com/translate/translate/blob/2.3.1/translate/storage/placeables/general.py#L115
 */
const pythonFormattingVariable = {
    rule: /(%(%|(\([^)]+\)){0,1}[-+0#]{0,1}(\d+|\*){0,1}(\.(\d+|\*)){0,1}[hlL]{0,1}[diouxXeEfFgGcrs]{1}))/ as RegExp,
    matchIndex: 0,
    tag: (x: string): React.ReactElement<React.ElementType> => {
        return (
            <Localized
                id='placeable-parser-pythonFormattingVariable'
                attrs={{ title: true }}
            >
                <mark
                    className='placeable'
                    title='Python string formatting variable'
                >
                    {x}
                </mark>
            </Localized>
        );
    },
};

export default pythonFormattingVariable;
