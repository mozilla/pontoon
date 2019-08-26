/* @flow */

import { Transformer } from 'fluent-syntax';

import type { FluentMessage } from './types';


/**
 * Return a copy of a given Fluent AST with all its text elements empty.
 *
 * This makes a copy of the given Fluent message, then walks the copy and
 * replaces the content of each TextElement it finds with an empty string.
 *
 * Note that this produces "junk" Fluent messages. Serializing the AST works,
 * but parsing it afterwards will result in a Junk message.
 *
 * @param {FluentMessage} source A Fluent AST to empty.
 * @returns {FluentMessage} An emptied copy of the source.
 */
export default function getEmptyMessage(source: FluentMessage): FluentMessage {
    class EmptyTransformer extends Transformer {
        visitTextElement(node) {
            node.value = '';
            return node;
        }
    }

    const message = source.clone();
    const transformer = new EmptyTransformer();
    return transformer.visit(message);
}
