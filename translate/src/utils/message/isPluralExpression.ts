import type { SelectExpression } from '@fluent/syntax';

import { CLDR_PLURALS } from '../constants';

/**
 * Return true when AST element represents a pluralized string.
 *
 * Keys of all variants of such elements are either CLDR plurals or numbers.
 */
export function isPluralExpression(
  expression: Readonly<SelectExpression>,
): boolean {
  return (
    expression?.type === 'SelectExpression' &&
    expression.variants.every(
      ({ key }) =>
        key.type === 'NumberLiteral' ||
        (key.name && CLDR_PLURALS.includes(key.name)),
    )
  );
}
