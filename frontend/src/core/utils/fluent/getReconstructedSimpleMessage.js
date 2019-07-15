import parser from './parser';


/**
 * Return a reconstructed Fluent message from the original message and some
 * translated content.
 */
export default function getReconstructedSimpleMessage(original, translation) {
    const message = parser.parseEntry(original);
    const key = message.id.name;

    const isMultilineTranslation = translation.indexOf('\n') > -1;

    let content;
    if (message.attributes && message.attributes.length === 1) {
        const attribute = message.attributes[0].id.name;

        if (isMultilineTranslation) {
            content = `${key} =\n    .${attribute} =`;
            translation.split('\n').forEach(t => content += `\n        ${t}`);
        }
        else {
            content = `${key} =\n    .${attribute} = ${translation}`;
        }
    }
    else {
        if (isMultilineTranslation) {
            content = `${key} =`;
            translation.split('\n').forEach(t => content += `\n    ${t}`);
        }
        else {
            content = `${key} = ${translation}`;
        }
    }
    return content;
}
