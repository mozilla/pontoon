/* @flow */

import { Transformer } from '@fluent/syntax';

import flattenMessage from './flattenMessage';
import isPluralExpression from './isPluralExpression';

import { CLDR_PLURALS } from 'core/plural';

import type { FluentMessage } from './types';
import type { Locale } from 'core/locale';

/**
 * Gather custom (numeric) plural variants
 */
function getNumericVariants(variants) {
    return variants.filter((variant) => {
        return variant.key.type === 'NumberLiteral';
    });
}

/**
 * Generate a CLDR template variant
 */
function getCldrTemplateVariant(variants) {
    return variants.find((variant) => {
        return CLDR_PLURALS.indexOf(variant.key.name) !== -1;
    });
}

/**
 * Generate locale plural variants from a template
 */
function getLocaleVariants(locale, template) {
    return locale.cldrPlurals.map((item) => {
        const localeVariant = template.clone();
        localeVariant.key.name = CLDR_PLURALS[item];
        localeVariant.default = false;
        return localeVariant;
    });
}

/**
 * Return variants with default variant set
 */
function withDefaultVariant(variants) {
    const defaultVariant = variants.find((variant) => {
        return variant.default === true;
    });

    if (!defaultVariant) {
        variants[variants.length - 1].default = true;
    }

    return variants;
}

/**
 * Return a copy of a given Fluent AST with all its simple elements empty and
 * plural variant keys set to given locale's CLDR plural categories. Such
 * messages are used to render the Rich Editor for untranslated strings.
 *
 * The algorithm makes a copy of the given Fluent message, flattens it, and
 * then walks it to make the required changes. The default variants are not
 * preserved.
 *
 * Note that this produces "junk" Fluent messages. Serializing the AST works,
 * but parsing it afterwards will result in a Junk message.
 *
 * @param {FluentMessage} source A Fluent AST to empty.
 * @returns {FluentMessage} An emptied copy of the source.
 */
export default function getEmptyMessage(
    source: FluentMessage,
    locale: Locale,
): FluentMessage {
    class EmptyTransformer extends Transformer {
        // Empty Text Elements
        visitTextElement(node) {
            node.value = '';
            return node;
        }

        // Create empty locale plural variants
        visitSelectExpression(node) {
            if (isPluralExpression(node)) {
                const variants = node.variants;
                const numericVariants = getNumericVariants(variants);

                const template = getCldrTemplateVariant(variants);
                const localeVariants = template
                    ? getLocaleVariants(locale, template)
                    : [];

                node.variants = withDefaultVariant(
                    numericVariants.concat(localeVariants),
                );
            }

            return this.genericVisit(node);
        }
    }

    const message = source.clone();

    // Convert all simple elements to TextElements
    const flatMessage = flattenMessage(message);

    // Empty TextElements
    const transformer = new EmptyTransformer();
    return transformer.visit(flatMessage);
}
