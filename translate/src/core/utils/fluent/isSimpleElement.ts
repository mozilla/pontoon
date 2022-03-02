import type { PatternElement } from '@fluent/syntax';

/**
 * Is ast element of type that can be presented as a simple string:
 * - TextElement
 * - Placeable with expression type StringLiteral, NumberLiteral,
 *   VariableReference, MessageReference, TermReference, FunctionReference
 */
export default function isSimpleElement(element: PatternElement): boolean {
    if (element.type === 'TextElement') {
        return true;
    }

    // Placeable
    if (element.type === 'Placeable') {
        switch (element.expression.type) {
            case 'FunctionReference':
            case 'TermReference':
            case 'MessageReference':
            case 'VariableReference':
            case 'NumberLiteral':
            case 'StringLiteral':
                return true;
            default:
                return false;
        }
    }

    return false;
}
