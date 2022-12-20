import {
  FluentSerializer,
  Pattern as FluentPattern,
  Placeable,
  StringLiteral,
  TextElement,
  Transformer,
} from '@fluent/syntax';
import { defaultFunctionMap, resourceToFluent } from '@messageformat/fluent';
import type { Message, Pattern, Variant } from 'messageformat';
import type { MessageEntry } from '.';

class SerializeTransformer extends Transformer {
  visitPattern(node: FluentPattern) {
    if (node.elements.length === 0) {
      node.elements.push(new Placeable(new StringLiteral('')));
      return node;
    } else {
      return this.genericVisit(node);
    }
  }
  visitTextElement(node: TextElement) {
    return node.value === '' ? new Placeable(new StringLiteral('')) : node;
  }
}

const serializer = new FluentSerializer();
const transformer = new SerializeTransformer();

/**
 * The default `FluentSerializer` produces source that cannot be re-parsed
 * for message values & attributes as well as selector variants with empty contents.
 * This custom wrapper will emit an empty escaped literal `{ "" }` for such cases.
 */
export function serializeEntry(entry: MessageEntry | null): string {
  if (!entry) {
    return '';
  }
  const data = new Map<string, Message>();
  if (entry.value) {
    data.set('', entry.value);
  }
  if (entry.attributes) {
    for (const [name, attr] of entry.attributes) {
      data.set(name, attr);
    }
  }
  const resource = new Map([[entry.id, data]]);
  const fnMap = { ...defaultFunctionMap, PLATFORM: 'PLATFORM' };
  const fr = resourceToFluent(resource, undefined, fnMap);

  transformer.visit(fr);
  return serializer.serialize(fr);
}

export function serializePattern(pattern: Pattern) {
  let res = '';
  for (const el of pattern.body) {
    if (el.type === 'text' || el.type === 'literal') {
      res += el.value;
    } else {
      throw new Error(`Unexpected ${el.type} element in pattern`);
    }
  }
  return res;
}
