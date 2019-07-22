import isSimpleElement from './isSimpleElement';


/**
 * Return true when AST has no value and a single attribute with only simple
 * elements.
 */
export default function isSimpleSingleAttributeMessage(ast) {
    if (
        ast &&
        !ast.value &&
        ast.attributes &&
        ast.attributes.length === 1 &&
        ast.attributes[0].value.elements.every(isSimpleElement)
    ) {
        return true;
    }

    return false;
}
