/* @flow */

import * as React from 'react';
import shortid from 'shortid';

import mark from './mark';


type Props = {
    children: ?string | Array<string | React.Node>,
};


type Parser = {
    rule: string | RegExp,
    tag: (string) => React.Element<any>,
};


/**
 * Returns a clone of the element returned by the tag function, but makes sure
 * that it has a `key` attribute.
 */
function enhanceTag(tag: (string) => React.Element<any>) {
    return (x: string) => {
        const elt = tag(x);
        return React.cloneElement(elt, { key: shortid.generate() });
    };
}


/**
 * Creates a React component class to mark content based on rules.
 *
 * The component takes its children and marks them using the rules of the
 * parsers that are provided.
 *
 * @param {Array<Parser>} parsers A list of Parser systems. A Parser must
 * define a `rule` and a `tag`. The `rule` can be either a string to match
 * terms or a RegExp. Note that a RegExp must have parentheses surrounding
 * your pattern, otherwise matches won't be captured. The `tag` is a function
 * that accepts a string (the matched term or pattern) and returns a React
 * element that will replace the match in the output.
 *
 * @returns {Array} An array of strings and React components, similar to the
 * original content but where each matching pattern has been replaced by a
 * marking component.
 */
export default function createMarker(parsers: Array<Parser>) {
    return class ContentMarker extends React.Component<Props> {
        render() {
            let content = this.props.children;

            if (!content) {
                return null;
            }

            for (let parser of parsers) {
                const tag = enhanceTag(parser.tag);
                content = mark(content, parser.rule, tag);
            }

            return content;
        }
    }
}
