/* @flow */

import { Transformer } from 'fluent-syntax';

import type { FluentMessage } from './types';


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
