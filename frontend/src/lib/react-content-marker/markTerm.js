/* @flow */

import * as React from 'react';


/**
 * Replaces matching terms in a string with markers.
 *
 * @param {string} content The content to parse and mark.
 *
 * @param {string} term The term to search and replace in the content. Case
 * sensitive.
 *
 * @param {Function} tag A function that takes the matched term and must return
 * a React component or a string. The value returned by that function will
 * replace the term in the output.
 *
 * @returns {Array} An array of strings and React components, similar to the
 * original content but where each matching term has been replaced by a
 * marking component.
 */
export default function markTerm(
    content: string,
    term: string,
    tag: (string) => React.Node
): Array<string | React.Node> {
    const output = [];

    const pos = content.indexOf(term);

    if (pos === -1) {
        return [content];
    }

    const parts = content.split(term);

    for (let i = 0; i < parts.length - 1; i++) {
        if (parts[i]) {
            output.push(parts[i]);
        }
        output.push(tag(term));
    }

    if (parts[parts.length - 1]) {
        output.push(parts[parts.length - 1]);
    }

    return output;
}
