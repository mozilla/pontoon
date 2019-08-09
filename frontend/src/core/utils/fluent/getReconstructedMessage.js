import { Transformer } from 'fluent-syntax';

import parser from './parser';


/**
 * Return a reconstructed Fluent message from the original message and some
 * translated content.
 */
export default function getReconstructedMessage(original, translation) {
    const message = parser.parseEntry(original);

    class ReplaceFirstTextTransformer extends Transformer {
        firstTextReplaced = false;

        visitTextElement(node) {
            if (!this.firstTextReplaced) {
                node.value = translation;
                this.firstTextReplaced = true;
            }
            else {
                node.value = '';
            }
            return node;
        }
    }

    const transformer = new ReplaceFirstTextTransformer();
    transformer.visit(message);

    return message;
}
