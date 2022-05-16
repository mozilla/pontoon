import {
  Attribute,
  Entry,
  FluentSerializer,
  Message,
  PatternElement,
  Placeable,
  StringLiteral,
  Transformer,
  Variant,
} from '@fluent/syntax';
import { flattenMessage } from './flattenMessage';

function replaceIfEmptyText(elements: PatternElement[]) {
  if (
    elements.length === 1 &&
    elements[0].type === 'TextElement' &&
    elements[0].value === ''
  ) {
    elements[0] = new Placeable(new StringLiteral(''));
  }
}

class SerializeTransformer extends Transformer {
  visitAttribute(node: Attribute) {
    replaceIfEmptyText(node.value.elements);
    return this.genericVisit(node);
  }

  visitMessage(node: Message) {
    if (node.value) {
      replaceIfEmptyText(node.value.elements);
    }
    return this.genericVisit(node);
  }

  visitVariant(node: Variant) {
    replaceIfEmptyText(node.value.elements);
    return this.genericVisit(node);
  }
}

const serializer = new FluentSerializer();
const transformer = new SerializeTransformer();

/**
 * The default `FluentSerializer` produces source that cannot be
 * re-parsed for message values & attributes as well as selector variants with empty contents.
 * This custom wrapper will emit an empty escaped literal `{ "" }` for such cases,
 * as well as always flattening messages when serialising.
 */
export function serializeEntry(entry: Entry) {
  const flatEntry = flattenMessage(entry);
  transformer.visit(flatEntry);
  return serializer.serializeEntry(flatEntry);
}
