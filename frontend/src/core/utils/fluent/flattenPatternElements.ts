import { TextElement, serializeExpression } from '@fluent/syntax';

import type { PatternElement } from '@fluent/syntax';

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
    const flatElements = [];
    let textFragments = [];

    elements.forEach((element) => {
        if (
            element.type === 'Placeable' &&
            element.expression &&
            element.expression.type === 'SelectExpression'
        ) {
            // Before adding SelectExpression merge any collected text fragments into a TextElement
            if (textFragments.length) {
                flatElements.push(new TextElement(textFragments.join('')));
                textFragments = [];
            }

            // Flatten SelectExpression variant elements
            element.expression.variants.forEach((variant) => {
                variant.value.elements = flattenPatternElements(
                    variant.value.elements,
                );
            });

            flatElements.push(element);
        } else {
            if (element.type === 'TextElement') {
                textFragments.push(element.value);
            } else {
                textFragments.push(serializeExpression(element));
            }
        }
    });

    // Merge any remaining collected text fragments into a TextElement
    if (textFragments.length) {
        flatElements.push(new TextElement(textFragments.join('')));
    }

    return flatElements;
}
