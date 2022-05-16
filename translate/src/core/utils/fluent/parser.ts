import {
  Attribute,
  FluentParser,
  Message,
  PatternElement,
  TextElement,
  Transformer,
  Variant,
} from '@fluent/syntax';

function replaceIfEmptyLiteral(elements: PatternElement[]) {
  if (
    elements.length === 1 &&
    elements[0].type === 'Placeable' &&
    elements[0].expression.type === 'StringLiteral' &&
    elements[0].expression.value === ''
  ) {
    elements[0] = new TextElement('');
  }
}

class SerializeTransformer extends Transformer {
  visitAttribute(node: Attribute) {
    replaceIfEmptyLiteral(node.value.elements);
    return this.genericVisit(node);
  }

  visitMessage(node: Message) {
    if (node.value) {
      replaceIfEmptyLiteral(node.value.elements);
    }
    return this.genericVisit(node);
  }

  visitVariant(node: Variant) {
    replaceIfEmptyLiteral(node.value.elements);
    return this.genericVisit(node);
  }
}

const parser = new FluentParser({ withSpans: false });
const transformer = new SerializeTransformer();

/**
 * To match the behaviour in our custom serializer,
 * this parses message values & attributes as well as selector variants
 * with an empty string literal `{ "" }` as their contents
 * as if they had an empty text element instead.
 */
export function parseEntry(source: string) {
  const entry = parser.parseEntry(source);
  transformer.visit(entry);
  return entry;
}
