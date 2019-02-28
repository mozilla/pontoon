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

    let remaining = content;
    let matches = rule.exec(remaining);

    while (matches) {
        // Use the last non-null matching form. This is to support several
        // capture groups in the rule.
        let match = matches.reduce((acc, cur) => cur || acc, '');

        const [previous, ...rest] = remaining.split(match);

        if (previous) {
            output.push(previous);
        }
        output.push(tag(match));

        // Compute the next step.
        remaining = rest.join(match);
        matches = rule.exec(remaining);
    }

    if (remaining) {
        output.push(remaining);
    }

    return output;
}
