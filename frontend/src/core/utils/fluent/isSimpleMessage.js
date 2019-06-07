import isSimpleElement from './isSimpleElement';


/**
 * Return true when AST represents a simple message.
 *
 * A simple message has no attributes and all value
 * elements are simple.
 */
export default function isSimpleMessage(ast) {
    if (
        ast &&
        ast.attributes &&
        !ast.attributes.length &&
        ast.value &&
        ast.value.elements.every(isSimpleElement)
    ) {
        return true;
    }

    return false;
}
