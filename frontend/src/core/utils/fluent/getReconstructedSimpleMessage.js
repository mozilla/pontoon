import parser from './parser';


/**
 * Return a reconstructed Fluent message from the original message and some
 * translated content.
 */
export default function getReconstructedSimpleMessage(original, translation) {
    const message = parser.parseEntry(original);
    const key = message.id.name;

    let content;
    if (message.attributes && message.attributes.length === 1) {
        const attribute = message.attributes[0].id.name;
        content = `${key} =\n    .${attribute} = ${translation}`;
    }
    else {
        content = `${key} = ${translation}`;
    }
    return content;
}
