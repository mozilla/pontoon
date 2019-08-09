import { Transformer } from 'fluent-syntax';


export default function getEmptyMessage(source) {
    class EmptyTransformer extends Transformer {
        visitTextElement(node) {
            node.value = '';
            return node;
        }
    }

    const message = source.clone();
    const transformer = new EmptyTransformer();
    return transformer.visit(message);
}
