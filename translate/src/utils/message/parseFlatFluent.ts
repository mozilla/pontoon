import {
  Attribute,
  Entry,
  FluentParser,
  Message,
  Pattern,
  serializeExpression,
  TextElement,
  Transformer,
} from '@fluent/syntax';

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
    node.value = node.value.replace(/{ "" }/g, '');
    return node;
  }
}

/**
 * Flattens the given Pattern, uplifting selectors to the highest possible level
 * and duplicating shared parts in the variants.
 *
 * Should only be called externally with the value of a Message or an Attribute.
 */
function flattenPatternElements(pattern: Pattern) {
  let text: TextElement | null = null;
  for (let i = 0; i < pattern.elements.length; ++i) {
    const element = pattern.elements[i];
    if (
      element.type === 'Placeable' &&
      element.expression &&
      element.expression.type === 'SelectExpression'
    ) {
      for (const variant of element.expression.variants) {
        flattenPatternElements(variant.value);
      }
      text = null;
    } else if (text) {
      text.value +=
        element.type === 'TextElement'
          ? element.value
          : serializeExpression(element);
      pattern.elements.splice(i, 1);
      i -= 1;
    } else if (element.type === 'TextElement') {
      text = element;
    } else {
      text = new TextElement(serializeExpression(element));
      pattern.elements[i] = text;
    }
  }
}

const parser = new FluentParser({ withSpans: false });
const transformer = new FlatParseTransformer();

/**
 * Custom wrapper for `new FluentParser().parseEntry()`
 *
 *   - All Placeables other than selects are serialised as TextElements
 *   - Empty String Literals `{ "" }` are parsed as empty TextElements
 */
export function parseFlatFluent(source: string): Entry {
  const fluentEntry = parser.parseEntry(source);
  transformer.visit(fluentEntry);
  return fluentEntry;
}
