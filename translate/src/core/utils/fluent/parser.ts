import {
  Attribute,
  FluentParser,
  Message,
  TextElement,
  Transformer,
} from '@fluent/syntax';

import { flattenPatternElements } from './flattenPatternElements';

class FlatParseTransformer extends Transformer {
  visitAttribute(node: Attribute) {
    flattenPatternElements(node.value);
    return this.genericVisit(node);
  }

  visitMessage(node: Message) {
    if (node.value) {
      flattenPatternElements(node.value);
    }
    return this.genericVisit(node);
  }

  visitTextElement(node: TextElement) {
    if (node.value === '{ "" }') {
      node.value = '';
    }
    return node;
  }
}

const parser = new FluentParser({ withSpans: false });
const transformer = new FlatParseTransformer();

/**
 * Custom wrapper for `new FluentParser().parseEntry()`
 *
 *   - Select expressions are lifted up to the highest possible level,
 *     duplicating shared contents as necessary.
 *   - All other Placeables are serialised as TextElements
 *   - Empty String Literals `{ "" }` are parsed as empty TextElements
 */
export function parseEntry(source: string) {
  const entry = parser.parseEntry(source);
  transformer.visit(entry);
  return entry;
}
