import {
  FluentSerializer,
  Pattern as FluentPattern,
  Placeable,
  StringLiteral,
  TextElement,
  Transformer,
} from '@fluent/syntax';
import { defaultFunctionMap, resourceToFluent } from '@messageformat/fluent';
import type { Message } from 'messageformat';
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
export function serializeEntry(
  format: string,
  entry: MessageEntry | null,
): string {
  if (!entry) {
    return '';
  }

  if (format !== 'ftl') {
    if (entry.value?.type !== 'message') {
      throw new Error(
        `Unsupported ${format} message type: ${entry.value?.type} [${entry.id}]`,
      );
    }
    let res = '';
    for (const el of entry.value.pattern.body) {
      if (el.type !== 'text') {
        throw new Error(
          `Unsupported ${format} element type: ${el.type} [${entry.id}]`,
        );
      }
      res += el.value;
    }
    return res;
  }

  const data = new Map<string, Message>();
  const fnMap: typeof defaultFunctionMap = {};
  if (entry.value) {
    data.set('', entry.value);
    addSelectorExpressions(fnMap, entry.value);
  }
  if (entry.attributes) {
    for (const [name, attr] of entry.attributes) {
      data.set(name, attr);
      addSelectorExpressions(fnMap, attr);
    }
  }
  const resource = new Map([[entry.id, data]]);
  Object.assign(fnMap, defaultFunctionMap);
  try {
    const fr = resourceToFluent(resource, undefined, fnMap);
    transformer.visit(fr);
    return serializer.serialize(fr);
  } catch {
    return '';
  }
}

function addSelectorExpressions(
  fnMap: typeof defaultFunctionMap,
  msg: Message,
) {
  if (msg.type === 'select') {
    for (let sel of msg.selectors) {
      if (sel.type === 'placeholder') {
        sel = sel.body;
      }
      if (sel.type === 'expression') {
        fnMap[sel.name] = sel.name;
      }
    }
  }
}
