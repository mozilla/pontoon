/* @flow */

import * as React from 'react';


/**
 * Replaces matching patterns in a string with markers.
 *
 * @param {string} content The content to parse and mark.
 *
 * @param {RegExp} rule The pattern to search and replace in the content.
 *
 * @param {Function} tag A function that takes the match string and must return
 * a React component or a string. The value returned by that function will
 * replace the term in the output.
 *
 * @returns {Array} An array of strings and React components, similar to the
 * original content but where each matching pattern has been replaced by a
 * marking component.
 */
export default function markRegExp(
    content: string,
    rule: RegExp,
    tag: (string) => React.Node
): Array<string | React.Node> {
    const output = [];

    const parts = content.split(rule);

    for (let i = 0; i < parts.length; i++) {
        if (!parts[i]) {
            continue;
        }

        if (i % 2) {
            output.push(tag(parts[i]));
        }
        else {
            output.push(parts[i]);
        }
    }

    return output;
}
