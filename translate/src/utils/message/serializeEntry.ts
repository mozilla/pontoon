import {
  FluentSerializer,
  Pattern as FluentPattern,
  Placeable,
  StringLiteral,
  TextElement,
  Transformer,
} from '@fluent/syntax';
import { resourceToFluent } from '@messageformat/fluent';
import { type Model, stringifyMessage } from 'messageformat';
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

  switch (format) {
    case 'ftl': {
      const data = new Map<string, Model.Message>();
      if (entry.value) {
        data.set('', entry.value);
      }
      if (entry.attributes) {
        for (const [name, attr] of entry.attributes) {
          data.set(name, attr);
        }
      }
      const resource = new Map([[entry.id, data]]);
      const functionMap = new Proxy(
        {},
        { get: (_, prop) => String(prop).toUpperCase() },
      );
      try {
        const fr = resourceToFluent(resource, { functionMap });
        transformer.visit(fr);
        return serializer.serialize(fr);
      } catch {
        return '';
      }
    }

    case 'po':
      return entry.value ? stringifyMessage(entry.value) : '';

    default: {
      if (entry.value?.type !== 'message') {
        throw new Error(
          `Unsupported ${format} message type: ${entry.value?.type} [${entry.id}]`,
        );
      }
      let res = '';
      for (const el of entry.value.pattern) {
        if (typeof el === 'string') {
          res += el;
        } else {
          throw new Error(
            `Unsupported ${format} element type: ${el.type} [${entry.id}]`,
          );
        }
      }
      return res;
    }
  }
}
