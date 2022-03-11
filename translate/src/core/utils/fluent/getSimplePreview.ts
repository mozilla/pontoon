import { Pattern, serializeExpression } from '@fluent/syntax';

import parser from './parser';

function serialize({ elements }: Pattern): string {
  let result = '';
  for (const elt of elements) {
    switch (elt.type) {
      case 'TextElement':
        result += elt.value;
        break;

      case 'Placeable':
        if (elt.expression.type === 'SelectExpression') {
          const { variants } = elt.expression;
          const dv = variants.find((v) => v.default) || variants[0];
          result += serialize(dv.value);
        } else {
          const expression = serializeExpression(elt.expression);
          result += `{ ${expression} }`;
        }
        break;
    }
  }
  return result;
}

/**
 * Turn a Fluent message into a simple string, without any syntax sigils.
 *
 * This function returns the most pertinent content that can be found in the
 * message, without the ID, attributes or selectors.
 *
 * For example:
 *   > my-message = Hello, World!
 *   "Hello, World!"
 *
 *   > my-selector =
 *   >     I like { $gender ->
 *   >        [male] him
 *   >        [female] her
 *   >       *[other] them
 *   >     }
 *   "I like them"
 *
 * @param {string} content A Fluent string to parse and simplify.
 *
 * @returns {string} A simplified version of the Fluent message, or the original
 * content if it isn't a valid Fluent message.
 */
export default function getSimplePreview(
  content: string | null | undefined,
): string {
  if (!content) return '';

  const message = parser.parseEntry(content);
  return message.type === 'Message' || message.type === 'Term'
    ? serialize(message.value || message.attributes[0].value)
    : content;
}
