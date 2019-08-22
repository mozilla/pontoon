/* @flow */

import isSimpleElement from './isSimpleElement';

/**
 * Return true when all elements are supported in rich FTL editor.
 *
 * Elements are supported if they are:
 * - simple elements or
 * - select expressions
 */
export default function areSupportedElements(elements: Array<Object>) {
    return elements.every(isSimpleElement);
    // We don't yet support Select Expressions, but soon.
    // return elements.every(element => {
    //     return (
    //         isSimpleElement(element) ||
    //         (
    //             element.type === 'Placeable' &&
    //             element.expression.type === 'SelectExpression' &&
    //             element.expression.variants.every(variant =>  {
    //                 return variant.value.elements.every(element => isSimpleElement(element));
    //             })
    //         )
    //     );
    // });
}
