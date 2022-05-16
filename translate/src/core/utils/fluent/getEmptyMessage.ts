import {
  BaseNode,
  Entry,
  SelectExpression,
  TextElement,
  Transformer,
  Variant,
} from '@fluent/syntax';

import type { Locale } from '~/context/Locale';

import { CLDR_PLURALS } from '../constants';
import { flattenMessage } from './flattenMessage';
import { isPluralExpression } from './isPluralExpression';

/**
 * Return a copy of a given Fluent AST with all its simple elements empty and
 * plural variant keys set to given locale's CLDR plural categories. Such
 * messages are used to render the Rich Editor for untranslated strings.
 *
 * The algorithm makes a copy of the given Fluent message, flattens it, and
 * then walks it to make the required changes. The default variants are not
 * preserved.
 *
 * @param {Entry} source A Fluent AST to empty.
 * @returns {Entry} An emptied copy of the source.
 */
export function getEmptyMessage(source: Entry, { cldrPlurals }: Locale): Entry {
  class EmptyTransformer extends Transformer {
    /** Create empty locale plural variants */
    visitSelectExpression(node: SelectExpression): BaseNode {
      if (isPluralExpression(node)) {
        const variants = node.variants;

        const res: Variant[] = [];
        let cldrTemplate: Variant | null = null;
        let hasDefault = false;
        for (const variant of variants) {
          const { key } = variant;
          if (key.type === 'NumberLiteral') {
            res.push(variant);
            hasDefault ||= variant.default;
          } else if (
            (!cldrTemplate || variant.default) &&
            key.type === 'Identifier' &&
            CLDR_PLURALS.indexOf(key.name) !== -1
          ) {
            cldrTemplate = variant;
          }
        }

        if (cldrTemplate) {
          cldrTemplate.default = false;
          for (const i of cldrPlurals) {
            const variant = cldrTemplate.clone();
            variant.key.name = CLDR_PLURALS[i];
            res.push(variant);
          }
        }
        if (!hasDefault && res.length > 0) {
          res[res.length - 1].default = true;
        }
        node.variants = res;
      }

      return this.genericVisit(node);
    }

    /** Empty Text Elements */
    visitTextElement(node: TextElement): TextElement {
      node.value = '';
      return node;
    }
  }

  const transformer = new EmptyTransformer();
  const flatMessage = flattenMessage(source);
  return transformer.visit(flatMessage) as any as Entry;
}
