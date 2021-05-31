import { serializeExpression } from '@fluent/syntax';
import type { PatternElement } from '@fluent/syntax';

type DeepStringArray = Array<DeepStringArray> | string | null;

/**
 * Returns a list of values from a Fluent AST.
 *
 * Walks the given elements' AST and return the most pertinent value for each.
 */
export default function serialize(
    elements: Array<PatternElement>,
): DeepStringArray {
    return elements.map(
        (elt): DeepStringArray => {
            if (elt.type === 'TextElement') {
                return elt.value;
            }

            if (elt.type === 'Placeable') {
                if (elt.expression.type === 'SelectExpression') {
                    const defaultVariants = elt.expression.variants.filter(
                        (v) => v.default,
                    );
                    return serialize(defaultVariants[0].value.elements);
                } else {
                    const expression = serializeExpression(elt.expression);
                    return `{ ${expression} }`;
                }
            }

            return null;
        },
    );
}
