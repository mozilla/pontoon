import isSimpleMessage from './isSimpleMessage';
import isSimpleSingleAttributeMessage from './isSimpleSingleAttributeMessage';
import isSupportedMessage from './isSupportedMessage';

import type { SyntaxType } from './types';
import type { Entry } from '@fluent/syntax';

/**
 * Return the syntax type of a given Fluent message.
 *
 * @param {Entry} message A Fluent message (AST) to analyze.
 *
 * @returns {string} The syntax type of the Fluent message. Can be one of:
 *      - "simple": can be shown as a simple string in generic editor;
 *      - "rich": can be shown in a rich editor;
 *      - "complex": can only be shown in a source editor.
 */
export default function getSyntaxType(message: Entry): SyntaxType {
    if (!isSupportedMessage(message)) {
        return 'complex';
    }

    if (isSimpleMessage(message) || isSimpleSingleAttributeMessage(message)) {
        return 'simple';
    }

    return 'rich';
}
