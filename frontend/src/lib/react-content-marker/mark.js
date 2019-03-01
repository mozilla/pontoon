/* @flow */

import * as React from 'react';

import markRegExp from './markRegExp';
import markTerm from './markTerm';


/**
 * Replaces matching patterns in a string with markers.
 *
 * @param {string | Array} content The content to parse and mark.
 *
 * @param {string | RegExp} rule The pattern to search and replace in the
 * content.
 *
 * @param {Function} tag A function that takes the match string and must return
 * a React component or a string. The value returned by that function will
 * replace the term in the output.
 *
 * @param {number} matchIndex The index of the match to use when marking with
 * a RegExp. If not provided, will use the last non-null match available.
 *
 * @returns {Array} An array of strings and React components, similar to the
 * original content but where each matching pattern has been replaced by a
 * marking component.
 */
export default function mark(
    content: string | Array<string | React.Node>,
    rule: string | RegExp,
    tag: (string) => React.Node,
    matchIndex: ?number,
): Array<string | React.Node> {
    if (!Array.isArray(content)) {
        content = [content];
    }

    if (!(rule instanceof RegExp || typeof rule === 'string')) {
        throw Error('Unsupported rule type for rule `' + rule + '`.');
    }

    const output = [];

    for (let part of content) {
        if (typeof part === 'string') {
            let marked;

            if (rule instanceof RegExp) {
                marked = markRegExp(part, rule, tag, matchIndex);
            }
            else if (typeof rule === 'string') {
                marked = markTerm(part, rule, tag);
            }

            output.push(marked);
        }
        else {
            output.push(part);
        }
    }

    return [].concat(...output);
}
