import { Transformer } from '@fluent/syntax';
import pseudoLocalization from 'pseudo-localization';

import { fluent } from 'core/utils';


class PseudoStringTransformer extends Transformer {
    visitTextElement(node) {
        node.value = pseudoLocalization.localize(node.value);
        return node;
    }
}


/**
 * Return an FTL file content with all text elements replaced with an accented
 * text version.
 *
 * This replaces all latin letters in the content into an accented Unicode
 * counterpart which doesn't impair readability. Some letters are doubled.
 *
 * For example, "Accented English" becomes "Ȧȧƈƈḗḗƞŧḗḗḓ Ḗḗƞɠŀīīşħ".
 *
 * Note that this doesn't preserve HTML tags in content.
 *
 * @param {string} content The content of an FTL file.
 *
 * @returns {string} The same file structure but pseudo-localized.
 */
export default function pseudoLocalizeResource(content: string) {
    const transformer = new PseudoStringTransformer();
    const resource = fluent.parser.parse(content);

    const pseudoBody = resource.body.map(entry => {
        return transformer.visit(entry);
    });

    resource.body = pseudoBody;

    return fluent.serializer.serialize(resource);
}
