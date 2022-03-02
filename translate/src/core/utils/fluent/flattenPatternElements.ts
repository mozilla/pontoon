import {
    PatternElement,
    SelectExpression,
    serializeExpression,
    TextElement,
} from '@fluent/syntax';

/**
 * Return a flattened list of Pattern elements.
 *
 * @param {Array<PatternElement>} elements A list of Pattern elements to flatten.
 *
 * @returns {Array<PatternElement>} An array containing elements of type
 * TextElement (merging serialized values of neighbour simple elements) and
 * Placeable (representing select expressions).
 */
export default function flattenPatternElements(
    elements: Array<PatternElement>,
): Array<PatternElement> {
    const flatElements: PatternElement[] = [];
    let textFragment = '';
    let prevSelect: SelectExpression | null = null;

    for (const element of elements) {
        if (
            element.type === 'Placeable' &&
            element.expression &&
            element.expression.type === 'SelectExpression'
        ) {
            // In a message with multiple SelectExpressions separated by some
            // whitespace, keep that whitespace out of select variants.
            if (/^\s+$/.test(textFragment)) {
                flatElements.push(new TextElement(textFragment));
                textFragment = '';
            }

            // Flatten SelectExpression variant elements
            for (const variant of element.expression.variants) {
                variant.value.elements = flattenPatternElements(
                    variant.value.elements,
                );

                // If there is preceding text, include that for all variants
                if (textFragment) {
                    const { elements } = variant.value;
                    const first = elements[0];
                    if (first?.type === 'TextElement') {
                        first.value = textFragment + first.value;
                    } else {
                        elements.unshift(new TextElement(textFragment));
                    }
                }
            }
            if (textFragment) textFragment = '';

            flatElements.push(element);
            prevSelect = element.expression;
        } else {
            let strValue =
                element.type === 'TextElement'
                    ? element.value
                    : serializeExpression(element);
            if (textFragment) {
                strValue = textFragment + strValue;
                textFragment = '';
            }

            if (prevSelect) {
                // Keep trailing whitespace out of variant values
                const wsEnd = strValue.match(/\s+$/);
                if (wsEnd) {
                    strValue = strValue.substring(0, wsEnd.index);
                    textFragment = wsEnd[0];
                }

                // If there is a preceding SelectExpression, append to each of its variants
                for (const variant of prevSelect.variants) {
                    const { elements } = variant.value;
                    const last = elements[elements.length - 1];
                    if (last?.type === 'TextElement') {
                        last.value += strValue;
                    } else {
                        elements.push(new TextElement(strValue));
                    }
                }
            } else {
                // ... otherwise, append to a temporary string
                textFragment += strValue;
            }
        }
    }

    // Merge any remaining collected text into a TextElement
    if (textFragment || flatElements.length === 0) {
        flatElements.push(new TextElement(textFragment));
    }

    return flatElements;
}
