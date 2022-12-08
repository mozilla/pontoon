import {
  Entry,
  FluentSerializer,
  Placeable,
  StringLiteral,
  TextElement,
  Transformer,
} from '@fluent/syntax';

class SerializeTransformer extends Transformer {
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
 *
 * **NOTE!** Modifies `entry`, so you may want to pass in a copy.
 */
export function serializeEntry(entry: Entry) {
  transformer.visit(entry);
  return serializer.serializeEntry(entry);
}
