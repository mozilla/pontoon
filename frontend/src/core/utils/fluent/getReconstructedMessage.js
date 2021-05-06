/* @flow */

import parser from './parser';

import type { Entry } from '@fluent/syntax';

/**
 * Return a reconstructed Fluent message from the original message and some
 * translated content.
 */
export default function getReconstructedMessage(
    original: string,
    translation: string,
): Entry {
    const message = parser.parseEntry(original);
    if (message.type !== 'Message' && message.type !== 'Term') {
        throw new Error(
            `Unexpected type '${message.type}' in getReconstructedMessage`,
        );
    }
    let key = message.id.name;

    // For Terms, the leading dash is removed in the identifier. We need to add
    // it back manually.
    if (message.type === 'Term') {
        key = '-' + key;
    }

    const isMultilineTranslation = translation.indexOf('\n') > -1;

    let content;

    if (message.attributes && message.attributes.length === 1) {
        const attribute = message.attributes[0].id.name;

        if (isMultilineTranslation) {
            content = `${key} =\n    .${attribute} =`;
            translation
                .split('\n')
                .forEach((t) => (content += `\n        ${t}`));
        } else {
            content = `${key} =\n    .${attribute} = ${translation}`;
        }
    } else {
        if (isMultilineTranslation) {
            content = `${key} =`;
            translation.split('\n').forEach((t) => (content += `\n    ${t}`));
        } else {
            content = `${key} = ${translation}`;
        }
    }

    return parser.parseEntry(content);
}
